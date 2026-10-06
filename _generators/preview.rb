#!/usr/bin/env ruby
# Local preview renderer for the LabX site.
#
# GitHub Pages builds this site with Jekyll, which cannot be installed on this
# host (no sudo, native gem builds fail). This script renders the same Liquid
# templates with the system `liquid` gem so every change can be reviewed before
# it is pushed. It implements only what this site uses: site data, the people
# collection, layouts, and parameter-free includes.
#
# Usage:  ruby _generators/preview.rb   ->  /tmp/labxscut-site-preview/
require 'liquid'
require 'yaml'
require 'fileutils'
require 'tmpdir'

ROOT = File.expand_path('..', __dir__)
OUT = ENV.fetch('LABX_PREVIEW_DIR') do
  File.join(Dir.tmpdir, 'labxscut-site-preview')
end
INCLUDES = File.join(ROOT, '_includes')
LAYOUTS = File.join(ROOT, '_layouts')

def read(path)
  File.read(path, encoding: 'UTF-8')
end

def front_matter(text)
  if text.start_with?("---\n") && (idx = text.index("\n---", 3))
    yaml = text[4..idx - 1]
    body = text[(idx + 4)..] || ''
    [YAML.safe_load(yaml, aliases: true) || {}, body]
  else
    [{}, text]
  end
end

def expand_includes(text, depth = 0)
  raise 'include recursion' if depth > 5
  text.gsub(/\{%\s*include\s+([\w\/.\-]+)\s*%\}/) do
    file = File.join(INCLUDES, Regexp.last_match(1))
    body = read(file)
    body = body.sub(/\A---\n.*?\n---\n/m, '')
    expand_includes(body, depth + 1)
  end
end

def render(text, env)
  Liquid::Template.error_mode = :strict
  Liquid::Template.parse(expand_includes(text)).render(env)
end

def wrap(content, layout_name, page_env, env)
  path = File.join(LAYOUTS, "#{layout_name}.html")
  raise "missing layout #{layout_name}" unless File.exist?(path)
  layout_env = { 'content' => content, 'page' => page_env, 'site' => env['site'] }
  body = read(path)
  inner, _ = front_matter(body)
  rendered = render(body, layout_env)
  if inner['layout']
    wrap(rendered, inner['layout'], page_env, env)
  else
    rendered
  end
end

config = YAML.safe_load(read(File.join(ROOT, '_config.yml'))) || {}
data = {}
Dir[File.join(ROOT, '_data', '*.yml')].sort.each do |path|
  data[File.basename(path, '.yml')] = YAML.safe_load(read(path), aliases: true) || []
end

people = Dir[File.join(ROOT, '_people', '*.md')].sort.map do |path|
  meta, = front_matter(read(path))
  meta['url'] = "/#{meta['nick']}/"
  meta
end

site = config.merge('data' => data, 'people' => people, 'time' => Time.now)
env = { 'site' => site }

PAGES = [
  'index.html',
  'tools/index.html',
  'people/index.html',
  'publications/index.html',
  'resources/index.html',
  '404.html'
].freeze

FileUtils.rm_rf(OUT)
FileUtils.mkdir_p(OUT)
rendered = 0

(PAGES + Dir[File.join(ROOT, '_people', '*.md')].map { |p| p.sub("#{ROOT}/", '') }).each do |rel|
  src = File.join(ROOT, rel)
  page, body = front_matter(read(src))
  page['url'] = rel == 'index.html' ? '/' : "/#{File.dirname(rel)}/"
  page['url'] = "/#{page['nick']}/" if page['nick']
  content = render(body, env.merge('page' => page))
  html = page['layout'] ? wrap(content, page['layout'], page, env) : content
  out_path =
    if page['nick']
      File.join(OUT, page['nick'], 'index.html')
    else
      File.join(OUT, rel.sub(/\.md\z/, '.html'))
    end
  FileUtils.mkdir_p(File.dirname(out_path))
  File.write(out_path, html)
  rendered += 1
end

FileUtils.cp_r(File.join(ROOT, 'assets'), OUT)
%w[deeplb sxLaep].each { |d| FileUtils.cp_r(File.join(ROOT, d), OUT) }

puts "preview: #{rendered} pages -> #{OUT}"

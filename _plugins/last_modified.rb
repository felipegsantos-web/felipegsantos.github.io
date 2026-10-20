# Sets `last_modified_at` on every page from git: the date of the latest commit that touched the page's own file or the
# content it is generated from (_data, _includes, _layouts). Used for <lastmod> in sitemap.xml.
# Needs the full git history (the workflow checks out with fetch-depth 0). Without git history no date is set and
# the sitemap leaves <lastmod> out, rather than using the build time.
require "open3"

module FelipeLastModified
  SHARED = %w[_data _includes _layouts].freeze

  def self.git_date(site, *paths)
    out, status = Open3.capture2("git", "-C", site.source, "log", "-1", "--format=%cI", "--", *paths, err: File::NULL)
    status.success? && !out.strip.empty? ? out.strip : nil
  rescue Errno::ENOENT
    nil
  end

  def self.shared_date(site)
    @shared ||= {}
    @shared[site.source] ||= git_date(site, *SHARED)
  end
end

Jekyll::Hooks.register :pages, :post_init do |page|
  next unless page.path =~ %r{\A(en|es)/}
  own = FelipeLastModified.git_date(page.site, page.path)
  shared = FelipeLastModified.shared_date(page.site)
  dates = [own, shared].compact.sort
  page.data["last_modified_at"] ||= dates.last unless dates.empty?
end

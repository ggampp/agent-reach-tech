from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_reach_tech import __version__
from agent_reach_tech.catalog import search as catalog_search
from agent_reach_tech.channels.cve_nvd import CveNvdChannel
from agent_reach_tech.channels.exa_search import ExaSearchChannel
from agent_reach_tech.channels.github import GitHubChannel
from agent_reach_tech.channels.hackernews import HackerNewsChannel
from agent_reach_tech.channels.lobsters import LobstersChannel
from agent_reach_tech.channels.osv import OsvChannel
from agent_reach_tech.channels.reddit import RedditChannel
from agent_reach_tech.channels.rss import RssChannel
from agent_reach_tech.channels.web import WebChannel
from agent_reach_tech.channels.youtube import YouTubeChannel
from agent_reach_tech.channels.registry import get_channel
from agent_reach_tech.config_loader import load_yaml
from agent_reach_tech.core.installer import build_install_report, execute_install_report
from agent_reach_tech.doctor import run_doctor
from agent_reach_tech.hooks.post_research import full_hook_output
from agent_reach_tech import research as research_api
from agent_reach_tech.triggers import load_triggers, route_message


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_doctor(_: argparse.Namespace) -> int:
    return run_doctor(standalone=True)


def cmd_install(args: argparse.Namespace) -> int:
    report = build_install_report(env=args.env, safe=args.safe, dry_run=args.dry_run)
    report = execute_install_report(report)

    print("")
    print(f"Install plan (env={args.env}, safe={args.safe}, dry_run={args.dry_run})")
    for action in report.actions:
        status = "EXEC" if action.executed else ("SKIP" if action.skipped else "PLAN")
        cmd = " ".join(action.command) if action.command else "(manual)"
        print(f"  [{status}] {action.description}")
        if action.command:
            print(f"         {cmd}")
        if action.reason:
            print(f"         reason: {action.reason}")

    if not args.dry_run:
        print("")
        print("Run: agent-reach-tech doctor")
    return 0


def cmd_hn(args: argparse.Namespace) -> int:
    hn = get_channel("hackernews") or HackerNewsChannel()
    if args.action == "front-page":
        _print_json(hn.front_page(args.limit))
    else:
        if not args.query:
            print("query required for search", file=sys.stderr)
            return 1
        _print_json(hn.search(args.query, args.limit))
    return 0


def cmd_lobsters(args: argparse.Namespace) -> int:
    lob = get_channel("lobsters") or LobstersChannel()
    _print_json(lob.hot(args.limit))
    return 0


def cmd_cve(args: argparse.Namespace) -> int:
    cve = get_channel("cve_nvd") or CveNvdChannel()
    if args.cve_id:
        result = cve.get_cve(args.cve_id)
        if not result:
            print(f"CVE not found: {args.cve_id}", file=sys.stderr)
            return 1
        _print_json(result)
    elif args.query:
        _print_json(cve.search(args.query, args.limit))
    else:
        print("Provide CVE-ID or --search QUERY", file=sys.stderr)
        return 1
    return 0


def cmd_osv(args: argparse.Namespace) -> int:
    if not args.ecosystem or not args.package:
        print("usage: agent-reach-tech osv <ecosystem> <package>", file=sys.stderr)
        return 1
    osv = get_channel("osv") or OsvChannel()
    _print_json(osv.query_package(args.ecosystem, args.package))
    return 0


def cmd_github(args: argparse.Namespace) -> int:
    gh_ch = get_channel("github") or GitHubChannel()
    try:
        if args.action == "repo":
            if not args.target:
                print("usage: agent-reach-tech github repo OWNER/REPO", file=sys.stderr)
                return 1
            _print_json(gh_ch.repo_view(args.target))
        elif args.action == "search":
            if not args.query:
                print("query required", file=sys.stderr)
                return 1
            if args.kind == "repos":
                _print_json(gh_ch.search_repos(args.query, args.limit))
            else:
                _print_json(gh_ch.search_issues(args.query, args.limit, repo=args.repo))
        return 0
    except (RuntimeError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1


def cmd_web(args: argparse.Namespace) -> int:
    web_ch = get_channel("web") or WebChannel()
    try:
        result = web_ch.read(args.url, raw=args.raw)
        if args.raw:
            print(result.get("content", ""))
        else:
            _print_json(result)
        return 0
    except (ValueError, Exception) as e:  # noqa: BLE001
        print(str(e), file=sys.stderr)
        return 1


def cmd_youtube(args: argparse.Namespace) -> int:
    yt = get_channel("youtube") or YouTubeChannel()
    try:
        if args.action == "info":
            _print_json(yt.info(args.target))
        elif args.action == "search":
            _print_json(yt.search(args.target, args.limit))
        else:
            _print_json(yt.subtitles(args.target, args.lang))
        return 0
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1


def cmd_rss(args: argparse.Namespace) -> int:
    rss = get_channel("rss") or RssChannel()
    try:
        if args.action == "list":
            _print_json(rss.list_curated())
        elif args.action == "category":
            _print_json(rss.read_category(args.target, args.limit))
        else:
            _print_json(rss.parse(args.target, args.limit))
        return 0
    except (RuntimeError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    exa = get_channel("exa_search") or ExaSearchChannel()
    query = args.query
    if args.profile and args.name:
        pass
    elif args.profile and not args.name:
        print("--name required when using --profile", file=sys.stderr)
        return 1
    if not query and not args.profile:
        print("query or --profile required", file=sys.stderr)
        return 1
    _print_json(
        exa.search(
            query or args.name or "",
            limit=args.limit,
            profile=args.profile,
            name=args.name,
        )
    )
    return 0


def cmd_reddit(args: argparse.Namespace) -> int:
    rd = get_channel("reddit") or RedditChannel()
    try:
        _print_json(rd.search(args.query, args.limit, subreddit=args.subreddit))
        return 0
    except Exception as e:  # noqa: BLE001
        print(str(e), file=sys.stderr)
        return 1


def cmd_catalog(args: argparse.Namespace) -> int:
    try:
        _print_json(catalog_search(args.term, limit=args.limit))
        return 0
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1


def cmd_feeds(_: argparse.Namespace) -> int:
    _print_json(load_yaml("feeds.yaml").get("feeds", {}))


def cmd_config(_: argparse.Namespace) -> int:
    _print_json(
        {
            "channels": load_yaml("channels.yaml"),
            "sources": load_yaml("sources.yaml"),
            "search_profiles": load_yaml("search-profiles.yaml"),
        }
    )
    return 0


def cmd_deps(_: argparse.Namespace) -> int:
    from agent_reach_tech.core.deps import check_all_deps

    _print_json([d.__dict__ for d in check_all_deps()])
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    result = route_message(" ".join(args.message))
    if args.json:
        _print_json(
            {
                "intent": result.intent,
                "label": result.label,
                "workflow": result.workflow,
                "commands": result.commands,
                "matched_keywords": result.matched_keywords,
                "confidence": result.confidence,
                "slash_commands": result.slash_commands,
            }
        )
    else:
        print(f"Intent: {result.intent} ({result.label})")
        print(f"Confidence: {result.confidence:.0%}")
        if result.matched_keywords:
            print(f"Matched: {', '.join(result.matched_keywords)}")
        print(f"Workflow: {result.workflow or '—'}")
        print("Suggested commands:")
        for cmd in result.commands:
            print(f"  agent-reach-tech {cmd}")
    return 0


def cmd_triggers(_: argparse.Namespace) -> int:
    _print_json(load_triggers())
    return 0


def cmd_research(args: argparse.Namespace) -> int:
    try:
        if args.kind == "oss":
            data = research_api.evaluate_oss(
                args.name,
                repo=args.repo,
                ecosystem=args.ecosystem,
                package=args.package,
            )
        elif args.kind == "cve":
            data = research_api.lookup_cve(args.name)
        elif args.kind == "discover":
            data = research_api.discover_oss(args.name)
        else:
            data = research_api.monitor_trends()
        if args.report:
            print(data.get("report", ""))
        else:
            _print_json(data)
        return 0
    except Exception as e:  # noqa: BLE001
        print(str(e), file=sys.stderr)
        return 1


def cmd_format(args: argparse.Namespace) -> int:
    try:
        if args.file:
            raw = Path(args.file).read_text(encoding="utf-8")
        else:
            raw = args.json or ""
        payload = json.loads(raw)
        print(full_hook_output(payload))
        return 0
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(str(e), file=sys.stderr)
        return 1


def cmd_mcp(_: argparse.Namespace) -> int:
    from agent_reach_tech.mcp_server import run_mcp

    return run_mcp()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-reach-tech",
        description="Standalone tech/security research CLI for coding agents",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check channels and dependencies").set_defaults(func=cmd_doctor)

    p_install = sub.add_parser("install", help="Install package, deps, and agent skill")
    p_install.add_argument("--env", choices=["auto", "local", "server"], default="auto")
    p_install.add_argument("--safe", action="store_true", help="Do not run system package managers")
    p_install.add_argument("--dry-run", action="store_true")
    p_install.set_defaults(func=cmd_install)

    p_hn = sub.add_parser("hn", help="Hacker News")
    p_hn.add_argument("action", choices=["front-page", "search"])
    p_hn.add_argument("query", nargs="?", default="")
    p_hn.add_argument("--limit", type=int, default=15)
    p_hn.set_defaults(func=cmd_hn)

    p_lob = sub.add_parser("lobsters", help="Lobste.rs")
    p_lob.add_argument("action", nargs="?", default="hot", choices=["hot"])
    p_lob.add_argument("--limit", type=int, default=15)
    p_lob.set_defaults(func=cmd_lobsters)

    p_cve = sub.add_parser("cve", help="CVE via NVD")
    p_cve.add_argument("cve_id", nargs="?", default="")
    p_cve.add_argument("--search", dest="query", default="")
    p_cve.add_argument("--limit", type=int, default=10)
    p_cve.set_defaults(func=cmd_cve)

    p_osv = sub.add_parser("osv", help="Package vulnerabilities via OSV.dev")
    p_osv.add_argument("ecosystem")
    p_osv.add_argument("package")
    p_osv.set_defaults(func=cmd_osv)

    p_gh = sub.add_parser("github", help="GitHub")
    gh_sub = p_gh.add_subparsers(dest="action", required=True)
    p_gh_repo = gh_sub.add_parser("repo")
    p_gh_repo.add_argument("target")
    p_gh_repo.set_defaults(func=cmd_github, kind=None, query=None, limit=10, repo=None)
    p_gh_search = gh_sub.add_parser("search")
    p_gh_search.add_argument("kind", choices=["repos", "issues"])
    p_gh_search.add_argument("query")
    p_gh_search.add_argument("--limit", type=int, default=10)
    p_gh_search.add_argument("--repo")
    p_gh_search.set_defaults(func=cmd_github, target=None)

    p_web = sub.add_parser("web", help="Read URL via Jina Reader")
    p_web.add_argument("url")
    p_web.add_argument("--raw", action="store_true")
    p_web.set_defaults(func=cmd_web)

    p_yt = sub.add_parser("youtube", help="YouTube via yt-dlp")
    yt_sub = p_yt.add_subparsers(dest="action", required=True)
    p_yt_info = yt_sub.add_parser("info", help="Video metadata")
    p_yt_info.add_argument("target")
    p_yt_info.add_argument("--lang", default="en")
    p_yt_info.set_defaults(func=cmd_youtube, limit=10)
    p_yt_search = yt_sub.add_parser("search", help="Search videos")
    p_yt_search.add_argument("target")
    p_yt_search.add_argument("--limit", type=int, default=10)
    p_yt_search.add_argument("--lang", default="en")
    p_yt_search.set_defaults(func=cmd_youtube)
    p_yt_subs = yt_sub.add_parser("subs", help="Subtitle info")
    p_yt_subs.add_argument("target")
    p_yt_subs.add_argument("--lang", default="en")
    p_yt_subs.add_argument("--limit", type=int, default=10)
    p_yt_subs.set_defaults(func=cmd_youtube)

    p_rss = sub.add_parser("rss", help="RSS feeds")
    rss_sub = p_rss.add_subparsers(dest="action", required=True)
    p_rss_list = rss_sub.add_parser("list", help="List curated feeds")
    p_rss_list.add_argument("target", nargs="?", default="")
    p_rss_list.set_defaults(func=cmd_rss, limit=15)
    p_rss_read = rss_sub.add_parser("read", help="Parse feed URL")
    p_rss_read.add_argument("target")
    p_rss_read.add_argument("--limit", type=int, default=15)
    p_rss_read.set_defaults(func=cmd_rss)
    p_rss_cat = rss_sub.add_parser("category", help="Read feeds by category")
    p_rss_cat.add_argument("target")
    p_rss_cat.add_argument("--limit", type=int, default=5)
    p_rss_cat.set_defaults(func=cmd_rss)

    p_search = sub.add_parser("search", help="Semantic search (Exa) with fallback")
    p_search.add_argument("query", nargs="?", default="")
    p_search.add_argument("--profile")
    p_search.add_argument("--name")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.set_defaults(func=cmd_search)

    p_rd = sub.add_parser("reddit", help="Reddit search (optional)")
    p_rd.add_argument("query")
    p_rd.add_argument("--limit", type=int, default=10)
    p_rd.add_argument("--subreddit")
    p_rd.set_defaults(func=cmd_reddit)

    p_cat = sub.add_parser("catalog", help="Search local open source catalog")
    cat_sub = p_cat.add_subparsers(dest="action", required=True)
    p_cat_search = cat_sub.add_parser("search")
    p_cat_search.add_argument("term")
    p_cat_search.add_argument("--limit", type=int, default=10)
    p_cat_search.set_defaults(func=cmd_catalog)

    p_route = sub.add_parser("route", help="Route user message to research intent")
    p_route.add_argument("message", nargs="+")
    p_route.add_argument("--json", action="store_true")
    p_route.set_defaults(func=cmd_route)

    sub.add_parser("triggers", help="Dump triggers.yaml").set_defaults(func=cmd_triggers)

    p_res = sub.add_parser("research", help="Orchestrated research with post-hook report")
    p_res.add_argument("kind", choices=["oss", "cve", "discover", "trends"])
    p_res.add_argument("name", nargs="?", default="")
    p_res.add_argument("--repo")
    p_res.add_argument("--ecosystem")
    p_res.add_argument("--package")
    p_res.add_argument("--report", action="store_true", help="Print markdown report only")
    p_res.set_defaults(func=cmd_research)

    p_fmt = sub.add_parser("format", help="Format research JSON to markdown + Engram hint")
    p_fmt.add_argument("--json", default="")
    p_fmt.add_argument("--file", help="JSON file path")
    p_fmt.set_defaults(func=cmd_format)

    sub.add_parser("mcp", help="Start MCP stdio server").set_defaults(func=cmd_mcp)

    sub.add_parser("feeds", help="List curated RSS feeds").set_defaults(func=cmd_feeds)
    sub.add_parser("config", help="Dump configuration").set_defaults(func=cmd_config)
    sub.add_parser("deps", help="List external dependencies").set_defaults(func=cmd_deps)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
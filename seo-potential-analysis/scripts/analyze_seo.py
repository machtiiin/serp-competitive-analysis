#!/usr/bin/env python3
"""
SEO Potential Analysis v2
ScreamingFrog + GSC Pages + GSC Coverage + GSC Queries + optional Hreflang
→ morefire-Design-Deck → PDF

Usage:
  python3 analyze_seo.py \
    --sf internal_html.csv \
    --gsc gsc_pages.csv \
    --brand "Mustermarke" \
    --domain "mustermarke.de" \
    --output ./mustermarke-seo-audit.html \
    [--gsc-coverage gsc_coverage.csv] \
    [--gsc-queries gsc_queries.csv] \
    [--sf-hreflang sf_hreflang.csv]
"""

import argparse, csv, os, re, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ── Design constants ──────────────────────────────────────────────────────────
C_RED    = "#DB3543"
C_ORANGE = "#f08262"
C_GREEN  = "#1d8348"
C_BLACK  = "#1d1d1b"
C_GREY   = "#edf0f1"
C_YELLOW = "#ffd433"
C_WHITE  = "#ffffff"
C_INK60  = "rgba(29,29,27,.62)"
C_INK40  = "rgba(29,29,27,.40)"
C_INK15  = "rgba(29,29,27,.15)"

# ── Column maps ───────────────────────────────────────────────────────────────
SF_COL = {
    "address":"url","Address":"url","URL":"url","url":"url",
    "status code":"status_code","Status Code":"status_code",
    "status":"status_text","Status":"status_text",
    "indexability":"indexable","Indexability":"indexable",
    "indexability status":"indexable_status","Indexability Status":"indexable_status",
    "title 1":"title","Title 1":"title",
    "title count":"title_count","Title Count":"title_count",
    "h1-1":"h1","H1-1":"h1",
    "h1-count":"h1_count","H1-Count":"h1_count","H1 Count":"h1_count",
    "word count":"word_count","Word Count":"word_count","Wortanzahl":"word_count",
    "content":"content_type","Content":"content_type",
    "content type":"content_type","Content Type":"content_type",
    # New columns
    "canonical link element 1":"canonical","Canonical Link Element 1":"canonical",
    "canonical":"canonical","Canonical":"canonical",
    "crawl depth":"crawl_depth","Crawl Depth":"crawl_depth","Crawltiefe":"crawl_depth",
    "inlinks":"inlinks","Inlinks":"inlinks",
}

GSC_COL = {
    "page":"url","Page":"url","seite":"url","Seite":"url",
    "clicks":"clicks","Clicks":"clicks","klicks":"clicks","Klicks":"clicks",
    "impressions":"impressions","Impressions":"impressions",
    "impressionen":"impressions","Impressionen":"impressions",
    "ctr":"ctr","CTR":"ctr",
    "position":"position","Position":"position",
    "durchschn. position":"position","Durchschn. Position":"position",
    "average position":"position",
}

QUERIES_COL = {
    "top queries":"query","Top queries":"query",
    "query":"query","Query":"query",
    "suchanfrage":"query","Suchanfrage":"query","Queries":"query",
    "clicks":"clicks","Clicks":"clicks","klicks":"clicks","Klicks":"clicks",
    "impressions":"impressions","Impressions":"impressions",
    "impressionen":"impressions","Impressionen":"impressions",
    "ctr":"ctr","CTR":"ctr",
    "position":"position","Position":"position",
}

COVERAGE_COL = {
    "url":"url","URL":"url","page":"url","Page":"url","seite":"url","Seite":"url",
    "status":"status","Status":"status",
    "coverage state":"status","Coverage State":"status",
    "coverage status":"status","Coverage Status":"status",
    "abdeckungsstatus":"status","reason":"status","Reason":"status",
    "grund":"status","Grund":"status",
    "indexing state":"status","Indexing State":"status",
    "letzte crawl-datum":"last_crawled","Last crawled":"last_crawled",
}

HREFLANG_COL = {
    "source":"source","Source":"source","url":"source","URL":"source","address":"source","Address":"source",
    "hreflang":"hreflang","Hreflang":"hreflang","language":"hreflang",
    "issue":"issue","Issue":"issue","problem":"issue","Problem":"issue","error":"issue","Error":"issue",
    "status":"issue","Status":"issue",
}

# GSC coverage status normalisation
COVERAGE_STATUS_NORM = {
    "crawled - currently not indexed":"crawled_not_indexed",
    "gecrawlt – derzeit nicht indexiert":"crawled_not_indexed",
    "gecrawlt - derzeit nicht indexiert":"crawled_not_indexed",
    "discovered - currently not indexed":"discovered_not_indexed",
    "gefunden – derzeit nicht indexiert":"discovered_not_indexed",
    "gefunden - derzeit nicht indexiert":"discovered_not_indexed",
    "soft 404":"soft_404",
    "weiche 404":"soft_404",
    "duplicate without user-selected canonical":"dup_no_canonical",
    "duplikat, kein kanonisches element vom nutzer ausgewählt":"dup_no_canonical",
    "duplikat, kein kanonisches element":"dup_no_canonical",
    "duplicate, submitted url not selected as canonical":"dup_not_selected",
    "duplikat, eingereichte url nicht als kanonisch ausgewählt":"dup_not_selected",
    "alternate page with proper canonical tag":"alt_canonical",
    "alternative seite mit richtigem kanonischem tag":"alt_canonical",
    "page with redirect":"redirect","seite mit weiterleitung":"redirect",
    "excluded by 'noindex' tag":"noindex",
    "durch 'noindex'-tag ausgeschlossen":"noindex",
    "durch noindex-tag ausgeschlossen":"noindex",
    "blocked by robots.txt":"robots","von robots.txt blockiert":"robots",
    "not found (404)":"not_found","nicht gefunden (404)":"not_found",
    "server error (5xx)":"server_error","serverfehler (5xx)":"server_error",
    "submitted and indexed":"indexed","submitted url indexed":"indexed",
    "indexed, not submitted in sitemap":"indexed",
    "indexiert, nicht in sitemap eingereicht":"indexed",
    "valid":"indexed",
}

# Q* tiers
Q_TIERS = [
    ("Sehr duenn",  "<100 Woerter",    0,   100,  C_RED),
    ("Duenn",       "100-299 Woerter", 100, 300,  C_ORANGE),
    ("Mittel",      "300-799 Woerter", 300, 800,  C_YELLOW),
    ("Reichhaltig", "800+ Woerter",    800, None, C_GREEN),
]

# CTR benchmarks by position range
CTR_BENCH = {1:0.25, 2:0.15, 3:0.10, 4:0.07, 5:0.06,
             6:0.05, 7:0.04, 8:0.035, 9:0.03, 10:0.025}

# ── Helpers ───────────────────────────────────────────────────────────────────

def read_csv_file(fp):
    for enc in ("utf-8-sig","utf-8","latin-1","cp1252"):
        for delim in (",","\t",";"):
            try:
                with open(fp, encoding=enc, newline="") as f:
                    rows = list(csv.reader(f, delimiter=delim))
                if len(rows)>1 and len(rows[0])>=2:
                    return rows
            except Exception:
                continue
    raise ValueError(f"Konnte {fp} nicht lesen.")

def norm_cols(headers, col_map):
    out = {}
    for i,h in enumerate(headers):
        key = h.strip().lstrip("﻿")
        norm = col_map.get(key) or col_map.get(key.lower())
        if norm and norm not in out:
            out[norm] = i
    return out

def gc(row, col, key, default=""):
    idx = col.get(key)
    if idx is None or idx >= len(row):
        return default
    return row[idx].strip()

def safe_int(v, d=0):
    try: return int(str(v).strip().replace(",","").replace(".",""))
    except: return d

def safe_float(v, d=0.0):
    try: return float(str(v).strip().replace("%","").replace(",","."))
    except: return d

def norm_url(url):
    url = url.strip()
    if url.startswith("http://"):
        url = "https://" + url[7:]
    return url.rstrip("/").lower()

def cluster_of(url):
    try:
        p = urlparse(url if "://" in url else "https://"+url)
        parts = [x for x in p.path.split("/") if x]
        if not parts: return "/ (Root)"
        seg = parts[0].lower()
        if "." in seg and seg.split(".")[-1] in ("pdf","doc","xls","ppt","zip","jpg","png","svg","gif"):
            return "/[Dateien]"
        return "/"+parts[0]+"/"
    except: return "/[Sonstige]"

def fmt(n):
    if n is None: return "-"
    return f"{n:,}".replace(",",".")

def pct(part, total, d=1):
    if not total: return 0.0
    return round(part/total*100, d)

def q_tier(wc):
    for name,_,lo,hi,_ in Q_TIERS:
        if hi is None:
            if wc >= lo: return name
        elif lo <= wc < hi: return name
    return None

def norm_coverage_status(raw):
    return COVERAGE_STATUS_NORM.get(raw.lower().strip(), "other")

# ── Data loading ──────────────────────────────────────────────────────────────

def load_sf(filepath):
    rows = read_csv_file(filepath)
    headers = [h.strip().lstrip("﻿") for h in rows[0]]
    col = norm_cols(headers, SF_COL)
    if "url" not in col:
        raise ValueError("Spalte 'Address'/'URL' nicht im SF-Export gefunden.")
    pages = []
    for row in rows[1:]:
        if not row or len(row)<2: continue
        url = gc(row,col,"url")
        if not url: continue
        sc = safe_int(gc(row,col,"status_code","0"))
        if sc == 0: continue
        idx_raw = gc(row,col,"indexable","Indexable")
        indexable = idx_raw.lower() in ("indexable","indexierbar","ja","yes","1","true")
        wc_raw = gc(row,col,"word_count","")
        word_count = safe_int(wc_raw) if wc_raw else None
        canonical_raw = gc(row,col,"canonical","")
        crawl_depth_raw = gc(row,col,"crawl_depth","")
        crawl_depth = safe_int(crawl_depth_raw) if crawl_depth_raw else None
        inlinks_raw = gc(row,col,"inlinks","")
        inlinks = safe_int(inlinks_raw) if inlinks_raw else None
        pages.append({
            "url":url, "url_norm":norm_url(url), "status_code":sc,
            "indexable":indexable,
            "title":gc(row,col,"title",""),
            "title_count":safe_int(gc(row,col,"title_count","1")),
            "h1":gc(row,col,"h1",""),
            "h1_count":safe_int(gc(row,col,"h1_count","1")),
            "word_count":word_count,
            "canonical":canonical_raw,
            "crawl_depth":crawl_depth,
            "inlinks":inlinks,
            "cluster":cluster_of(url),
        })
    return pages

def load_gsc(filepath):
    rows = read_csv_file(filepath)
    headers = [h.strip().lstrip("﻿") for h in rows[0]]
    col = norm_cols(headers, GSC_COL)
    if "url" not in col: col["url"] = 0
    data = {}
    for row in rows[1:]:
        if not row: continue
        url = gc(row,col,"url")
        if not url: continue
        data[norm_url(url)] = {
            "clicks":safe_int(gc(row,col,"clicks","0")),
            "impressions":safe_int(gc(row,col,"impressions","0")),
            "position":safe_float(gc(row,col,"position","0")),
            "ctr":safe_float(gc(row,col,"ctr","0")),
        }
    return data

def load_gsc_queries(filepath):
    rows = read_csv_file(filepath)
    headers = [h.strip().lstrip("﻿") for h in rows[0]]
    col = norm_cols(headers, QUERIES_COL)
    if "query" not in col: col["query"] = 0
    data = []
    for row in rows[1:]:
        if not row: continue
        query = gc(row,col,"query")
        if not query: continue
        pos = safe_float(gc(row,col,"position","0"))
        imp = safe_int(gc(row,col,"impressions","0"))
        clk = safe_int(gc(row,col,"clicks","0"))
        ctr = safe_float(gc(row,col,"ctr","0"))
        data.append({"query":query,"clicks":clk,"impressions":imp,"ctr":ctr,"position":pos})
    return data

def load_gsc_coverage(filepath):
    """
    GSC Coverage export: may have columns URL+Status or just status in first col.
    Returns dict: status_key -> list of URLs
    """
    rows = read_csv_file(filepath)
    headers = [h.strip().lstrip("﻿") for h in rows[0]]
    col = norm_cols(headers, COVERAGE_COL)

    result = defaultdict(list)
    # Detect format: if we have a status column use it, else try first non-URL col
    for row in rows[1:]:
        if not row: continue
        url = gc(row,col,"url","")
        status_raw = gc(row,col,"status","")
        if not status_raw and len(row) >= 2:
            # Try second column as status
            status_raw = row[1].strip() if "url" in col and col["url"]==0 else row[0].strip()
        if not url and not status_raw: continue
        status_key = norm_coverage_status(status_raw)
        if url:
            result[status_key].append(norm_url(url))
    return dict(result)

def load_sf_hreflang(filepath):
    """
    SF hreflang export: columns Source, hreflang value, status/issue.
    Returns summary dict with issue counts.
    """
    rows = read_csv_file(filepath)
    if len(rows) < 2: return {}
    headers = [h.strip().lstrip("﻿") for h in rows[0]]
    col = norm_cols(headers, HREFLANG_COL)
    issues = defaultdict(int)
    total = 0
    for row in rows[1:]:
        if not row: continue
        total += 1
        issue = gc(row,col,"issue","").lower()
        if issue and issue not in ("ok","valid","gueltig","kein fehler"):
            issues[issue] += 1
    return {"total": total, "issues": dict(issues)}

# ── Core metrics ──────────────────────────────────────────────────────────────

def compute(pages, gsc, coverage=None, queries=None, hreflang=None):
    total = len(pages)
    if not total: return {}

    alive   = [p for p in pages if 200 <= p["status_code"] < 300]
    err_4xx = [p for p in pages if 400 <= p["status_code"] < 500]
    err_5xx = [p for p in pages if 500 <= p["status_code"] < 600]
    redir   = [p for p in pages if 300 <= p["status_code"] < 400]

    indexable = [p for p in alive if p["indexable"]]
    idx_set   = {p["url_norm"] for p in indexable}

    with_imp = {u:d for u,d in gsc.items() if u in idx_set and d["impressions"]>0}
    relevant = {u:d for u,d in gsc.items() if u in idx_set and d["clicks"]>=10}

    # Hygiene
    missing_title = [p for p in indexable if not p["title"]]
    missing_h1    = [p for p in indexable if not p["h1"] or p["h1_count"]==0]
    multi_h1      = [p for p in indexable if p["h1_count"]>1]
    title_seen    = defaultdict(list)
    for p in indexable:
        if p["title"]: title_seen[p["title"].lower()].append(p)
    dup_title = [p for ps in title_seen.values() if len(ps)>1 for p in ps]
    hygiene_urls = set()
    for p in missing_title+dup_title+missing_h1+multi_h1:
        hygiene_urls.add(p["url_norm"])

    # Q* word count
    wc_pages = [p for p in indexable if p["word_count"] is not None]
    has_wc   = len(wc_pages)>0
    q_dist   = {name:0 for name,*_ in Q_TIERS}
    thin_set = set()
    if has_wc:
        for p in wc_pages:
            tier = q_tier(p["word_count"])
            if tier and tier in q_dist: q_dist[tier]+=1
            if p["word_count"]<300: thin_set.add(p["url_norm"])
    thin_with_imp    = sum(1 for u in thin_set if u in with_imp)
    thin_without_imp = len(thin_set)-thin_with_imp

    # ── NEW: Canonical analysis ───────────────────────────────────────────────
    has_canonical_data = any(p["canonical"] for p in indexable)
    canon_self     = []
    canon_external = []
    canon_missing  = []
    if has_canonical_data:
        for p in indexable:
            c = p["canonical"].strip()
            if not c:
                canon_missing.append(p)
            elif norm_url(c) == p["url_norm"]:
                canon_self.append(p)
            else:
                canon_external.append(p)
    # Indexable pages with canonical pointing elsewhere = potential confusion
    canon_conflict = canon_external  # indexable but canon says different URL

    # ── NEW: Crawl depth analysis ─────────────────────────────────────────────
    has_depth_data = any(p["crawl_depth"] is not None for p in indexable)
    depth_dist = {"1-2":0, "3-4":0, "5+":0}
    deep_pages = []  # depth >= 5
    if has_depth_data:
        for p in indexable:
            d = p["crawl_depth"]
            if d is None: continue
            if d <= 2:   depth_dist["1-2"]+=1
            elif d <= 4: depth_dist["3-4"]+=1
            else:        depth_dist["5+"]+=1; deep_pages.append(p)

    # ── NEW: Orphan pages (0 inlinks) ─────────────────────────────────────────
    has_inlinks_data = any(p["inlinks"] is not None for p in indexable)
    orphan_pages = []
    if has_inlinks_data:
        orphan_pages = [p for p in indexable if p["inlinks"] is not None and p["inlinks"]==0]

    # ── NEW: CTR anomaly detection (from existing GSC pages data) ────────────
    ctr_opportunities = []  # good position, low CTR
    low_hanging = []        # position 4-10, high impressions
    for url_norm, d in gsc.items():
        if url_norm not in idx_set: continue
        pos  = d["position"]
        imp  = d["impressions"]
        clk  = d["clicks"]
        ctr_val = d["ctr"] if d["ctr"] > 0 else (clk/imp if imp>0 else 0)
        if pos < 1 or pos > 10: continue
        pos_int = max(1, min(10, int(round(pos))))
        bench   = CTR_BENCH.get(pos_int, 0.025)
        if imp >= 50 and ctr_val < bench * 0.5:  # CTR less than half benchmark
            ctr_opportunities.append({
                "url":url_norm, "position":pos, "impressions":imp,
                "clicks":clk, "ctr":ctr_val, "benchmark":bench,
                "cluster":cluster_of(url_norm),
            })
        if 4 <= pos <= 10 and imp >= 100:
            low_hanging.append({
                "url":url_norm, "position":pos, "impressions":imp,
                "clicks":clk, "ctr":ctr_val, "cluster":cluster_of(url_norm),
            })

    ctr_opportunities.sort(key=lambda x: -x["impressions"])
    low_hanging.sort(key=lambda x: -x["impressions"])

    # Group CTR opportunities by cluster
    ctr_by_cluster = defaultdict(lambda: {"count":0,"impressions":0})
    for item in ctr_opportunities:
        c = item["cluster"]
        ctr_by_cluster[c]["count"]+=1
        ctr_by_cluster[c]["impressions"]+=item["impressions"]

    # ── NEW: GSC Coverage analysis ────────────────────────────────────────────
    cov = {}
    if coverage:
        for status_key, urls in coverage.items():
            cov[status_key] = len(urls)
        # Group non-indexed types
    crawled_not_indexed    = cov.get("crawled_not_indexed", 0)
    discovered_not_indexed = cov.get("discovered_not_indexed", 0)
    soft_404               = cov.get("soft_404", 0)
    dup_no_canonical       = cov.get("dup_no_canonical", 0) + cov.get("dup_not_selected", 0)
    alt_canonical          = cov.get("alt_canonical", 0)
    total_not_indexed_gsc  = crawled_not_indexed + discovered_not_indexed + soft_404

    # ── NEW: Query analysis ───────────────────────────────────────────────────
    top_low_hanging_queries = []
    if queries:
        q_sorted = sorted([q for q in queries if 4<=q["position"]<=10 and q["impressions"]>=50],
                          key=lambda x: -x["impressions"])
        top_low_hanging_queries = q_sorted[:8]

    # ── Cluster analysis ──────────────────────────────────────────────────────
    cdata = defaultdict(lambda:{
        "total":0,"indexable":0,"err4":0,"err5":0,
        "impressions":0,"clicks":0,"positions":[],"thin":0,"wc_pages":0,
        "crawled_not_indexed":0,"ctr_issues":0,
    })
    for p in pages:
        c = p["cluster"]
        cdata[c]["total"]+=1
        if p["indexable"] and 200<=p["status_code"]<300: cdata[c]["indexable"]+=1
        if 400<=p["status_code"]<500: cdata[c]["err4"]+=1
        if 500<=p["status_code"]<600: cdata[c]["err5"]+=1
        if p["word_count"] is not None:
            cdata[c]["wc_pages"]+=1
            if p["word_count"]<300: cdata[c]["thin"]+=1
        d = gsc.get(p["url_norm"])
        if d:
            cdata[c]["impressions"]+=d["impressions"]
            cdata[c]["clicks"]+=d["clicks"]
            if d["position"]>0: cdata[c]["positions"].append(d["position"])

    # Add coverage issues to clusters
    if coverage:
        for status_key in ("crawled_not_indexed","discovered_not_indexed","soft_404"):
            for url in coverage.get(status_key,[]):
                c = cluster_of(url)
                cdata[c]["crawled_not_indexed"]+=1

    # Add CTR issues to clusters
    for item in ctr_opportunities:
        cdata[item["cluster"]]["ctr_issues"]+=1

    clusters = []
    for cname,d in cdata.items():
        if d["total"]<2: continue
        avg_pos   = round(sum(d["positions"])/len(d["positions"]),1) if d["positions"] else 0
        thin_pct  = pct(d["thin"],d["wc_pages"]) if d["wc_pages"] else None
        err_pct   = pct(d["err4"]+d["err5"],d["total"])
        n_idx     = d["indexable"]; n_imp = d["impressions"]
        not_idx   = d["crawled_not_indexed"]

        if err_pct>=30:
            rec = ("FEHLER",    C_RED,    "Viele Fehler-URLs")
        elif n_idx>=5 and n_imp==0 and not_idx==0:
            rec = ("DEINDEX",   C_RED,    "Keine Sichtbarkeit")
        elif not_idx >= 3 and n_imp==0:
            rec = ("DEINDEX",   C_RED,    "Google indexiert nicht")
        elif n_idx>=3 and n_imp>0 and thin_pct is not None and thin_pct>60 and avg_pos>15:
            rec = ("OPTIMIEREN",C_ORANGE, "Potenzial vorhanden")
        elif d["ctr_issues"]>=3:
            rec = ("CTR",       C_ORANGE, "CTR-Optimierung")
        elif n_idx>=3 and n_imp>0 and (avg_pos==0 or avg_pos<=10):
            rec = ("STARK",     C_GREEN,  "Gut sichtbar")
        else:
            rec = ("MONITOR",   C_INK40,  "Gemischte Signale")

        clusters.append({
            "name":cname,"total":d["total"],"indexable":n_idx,
            "impressions":n_imp,"clicks":d["clicks"],"avg_position":avg_pos,
            "thin_pct":thin_pct,"error_pct":err_pct,"not_indexed":not_idx,
            "ctr_issues":d["ctr_issues"],"rec":rec,
        })

    order = {"FEHLER":0,"DEINDEX":1,"OPTIMIEREN":2,"CTR":3,"STARK":4,"MONITOR":5}
    clusters.sort(key=lambda x:(order.get(x["rec"][0],9),-x["total"]))

    return {
        "total":total,"alive":len(alive),
        "err_4xx":len(err_4xx),"err_5xx":len(err_5xx),"redir":len(redir),
        "indexable":len(indexable),
        "with_imp":len(with_imp),"relevant":len(relevant),
        "missing_title":len(missing_title),"dup_title":len(dup_title),
        "missing_h1":len(missing_h1),"multi_h1":len(multi_h1),
        "hygiene_issues":len(hygiene_urls),
        "has_wc":has_wc,"q_dist":q_dist,"wc_pages":len(wc_pages),
        "thin_with_imp":thin_with_imp,"thin_without_imp":thin_without_imp,
        "total_thin":len(thin_set),
        # Canonical
        "has_canonical_data":has_canonical_data,
        "canon_self":len(canon_self),"canon_external":len(canon_external),
        "canon_missing":len(canon_missing),"canon_conflict":len(canon_conflict),
        # Crawl depth
        "has_depth_data":has_depth_data,"depth_dist":depth_dist,
        "deep_pages":len(deep_pages),
        # Orphans
        "has_inlinks_data":has_inlinks_data,"orphan_pages":len(orphan_pages),
        # CTR
        "ctr_opportunities":ctr_opportunities[:10],
        "low_hanging":low_hanging[:8],
        "ctr_by_cluster":sorted(ctr_by_cluster.items(),key=lambda x:-x[1]["impressions"])[:6],
        # Coverage
        "has_coverage":bool(coverage),
        "crawled_not_indexed":crawled_not_indexed,
        "discovered_not_indexed":discovered_not_indexed,
        "soft_404":soft_404,
        "dup_no_canonical":dup_no_canonical,
        "alt_canonical":alt_canonical,
        "total_not_indexed_gsc":total_not_indexed_gsc,
        # Queries
        "top_low_hanging_queries":top_low_hanging_queries,
        # Hreflang
        "has_hreflang":bool(hreflang),
        "hreflang_data":hreflang or {},
        # Clusters
        "clusters":clusters[:16],
        "deindex_clusters": [c for c in clusters if c["rec"][0]=="DEINDEX"][:6],
        "optimize_clusters":[c for c in clusters if c["rec"][0] in ("OPTIMIEREN","CTR")][:6],
    }

# ── SVG helpers ───────────────────────────────────────────────────────────────

def svg_funnel(levels):
    bar_h,gap = 44,14
    lw,bw,nw  = 340,820,200
    tw = lw+bw+nw
    th = len(levels)*(bar_h+gap)-gap
    max_c = levels[0][1] if levels else 1
    lines = [f'<svg viewBox="0 0 {tw} {th}" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block;">']
    for i,(label,count,p,color) in enumerate(levels):
        y = i*(bar_h+gap)
        bar_px = max(8,int(count/max(max_c,1)*bw))
        lines.append(f'<text x="{lw-18}" y="{y+bar_h//2+8}" text-anchor="end" font-family="Heebo,sans-serif" font-size="21" fill="{C_INK60}">{label}</text>')
        lines.append(f'<rect x="{lw}" y="{y}" width="{bar_px}" height="{bar_h}" rx="3" fill="{color}"/>')
        if bar_px>140:
            lines.append(f'<text x="{lw+bar_px-14}" y="{y+bar_h//2+8}" text-anchor="end" font-family="Heebo,sans-serif" font-size="21" font-weight="700" fill="white">{fmt(count)}</text>')
        else:
            lines.append(f'<text x="{lw+bar_px+12}" y="{y+bar_h//2+8}" font-family="Heebo,sans-serif" font-size="21" font-weight="700" fill="{C_BLACK}">{fmt(count)}</text>')
        pct_str = "100 %" if i==0 else f"{p:.1f} %"
        lines.append(f'<text x="{lw+bw+nw-14}" y="{y+bar_h//2+8}" text-anchor="end" font-family="Heebo,sans-serif" font-size="19" fill="{C_INK40}">{pct_str}</text>')
    lines.append("</svg>")
    return "\n".join(lines)

def svg_stacked_bar(segments, total, width=1200, height=56):
    if not total:
        return f'<p style="color:{C_INK40};font-size:20px;">Keine Wortanzahl-Daten verfuegbar.</p>'
    lines = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="width:100%;">']
    x = 0
    for _,count,color in segments:
        w = int(count/total*width)
        if w>0: lines.append(f'<rect x="{x}" y="0" width="{w}" height="{height}" fill="{color}"/>')
        x+=w
    if x<width: lines.append(f'<rect x="{x}" y="0" width="{width-x}" height="{height}" fill="{segments[-1][2]}"/>')
    lines.append("</svg>")
    return "\n".join(lines)

# ── Component helpers ─────────────────────────────────────────────────────────

def find_row(icon_color, title, desc, pill_text, pill_class, last=False):
    ico = {
        C_RED:   '<circle cx="12" cy="12" r="10" fill="var(--c-red)"/><path d="M8 8 L16 16 M16 8 L8 16" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
        C_ORANGE:'<circle cx="12" cy="12" r="10" fill="var(--c-orange)"/><line x1="8" y1="12" x2="16" y2="12" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>',
        C_GREEN: '<circle cx="12" cy="12" r="10" fill="var(--c-green)"/><path d="M8 12.5 L11 15.5 L16.5 9.5" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    }.get(icon_color,"")
    border = "border-bottom:0;" if last else ""
    return (f'<div class="find-row" style="{border}">'
            f'<svg viewBox="0 0 24 24" fill="none" class="ico">{ico}</svg>'
            f'<div><div class="label-title">{title}</div><div class="label-desc">{desc}</div></div>'
            f'<div class="pill {pill_class}">{pill_text}</div></div>')

def footer(brand, domain):
    return (f'<div class="footer"><span>{brand} | SEO-Potenzialanalyse &middot; {domain}</span>'
            f'<img class="logo" src="https://www.more-fire.com/wp-content/uploads/2020/09/morefire-logo-farbig.svg" alt="more-fire"/></div>')

def footer_white(brand, domain):
    return (f'<div class="footer"><span style="color:rgba(255,255,255,.5);">{brand} | SEO-Potenzialanalyse &middot; {domain}</span>'
            f'<img class="logo" src="https://www.more-fire.com/wp-content/uploads/2020/09/morefire-logo-white.svg" alt="more-fire"/></div>')

def stat_block(value, label, color=C_RED):
    return (f'<div style="display:flex;flex-direction:column;gap:6px;">'
            f'<p class="ch-stat" style="color:{color};">{value}</p>'
            f'<div style="font-size:20px;color:{C_INK60};font-weight:500;line-height:1.3;">{label}</div>'
            f'</div>')

# ── HTML deck generator ───────────────────────────────────────────────────────

def generate_html(m, brand, domain, crawl_date):
    total=m["total"]; indexable=m["indexable"]

    # Executive summary
    exec_rows = []
    err_total = m["err_4xx"]+m["err_5xx"]
    if err_total>0:
        exec_rows.append((C_RED,f'Harte Fehler: {fmt(err_total)} Seiten ({pct(err_total,total):.1f}%)',
            f'{fmt(m["err_4xx"])} x 4xx, {fmt(m["err_5xx"])} x 5xx. Direkte Crawl-Budget- und Indexierungsverluste.',"Fix","gap"))
    else:
        exec_rows.append((C_GREEN,"Keine harten Fehler","Alle Seiten antworten mit gueltigen Status-Codes.","OK","ok"))

    h_pct = pct(m["hygiene_issues"],indexable)
    if h_pct>10:
        exec_rows.append((C_ORANGE,f'On-Page-Hygiene: {h_pct:.0f}% betroffen',
            f'{fmt(m["missing_title"])} ohne Titel, {fmt(m["dup_title"])} doppelter Titel, {fmt(m["missing_h1"])} ohne H1.',"Review","warn"))

    invisible = indexable-m["with_imp"]
    if invisible>0 and indexable>0:
        inv_pct = pct(invisible,indexable)
        exec_rows.append((C_ORANGE if inv_pct<50 else C_RED,
            f'{inv_pct:.0f}% der indexierbaren Seiten ohne jede GSC-Sichtbarkeit',
            f'{fmt(invisible)} von {fmt(indexable)} indexierbaren Seiten haben null Impressionen.  ',
            "Review" if inv_pct<50 else "Fix","warn" if inv_pct<50 else "gap"))

    if m["has_wc"] and m["total_thin"]>0:
        tp = pct(m["total_thin"],m["wc_pages"])
        exec_rows.append((C_ORANGE if tp<40 else C_RED,
            f'Content-Qualitaet: {tp:.0f}% aller Seiten duenn oder sehr duenn',
            f'{fmt(m["total_thin"])} Seiten unter 300 Woerter. {fmt(m["thin_without_imp"])} davon ohne GSC-Impressionen.',
            "Review" if tp<40 else "Fix","warn" if tp<40 else "gap"))

    if m["has_coverage"] and m["total_not_indexed_gsc"]>0:
        exec_rows.append((C_RED,
            f'GSC: {fmt(m["total_not_indexed_gsc"])} Seiten gecrawlt oder gefunden aber nicht indexiert',
            f'{fmt(m["crawled_not_indexed"])} gecrawlt-nicht-indexiert (Content-Qualitaetssignal), '
            f'{fmt(m["discovered_not_indexed"])} gefunden-nicht-indexiert (Crawl-Budget), '
            f'{fmt(m["soft_404"])} Soft-404.',"Fix","gap"))

    if len(exec_rows)<5 and len(m["ctr_opportunities"])>=5:
        exec_rows.append((C_ORANGE,
            f'{len(m["ctr_opportunities"])} Seiten mit CTR deutlich unter Benchmark',
            f'Gut positionierte Seiten (Top 10) mit ungewoehnlich niedriger Klickrate. Title-/Meta-Optimierungspotenzial.',"Review","warn"))

    exec_rows = exec_rows[:5]
    exec_html = "".join(find_row(r[0],r[1],r[2],r[3],r[4],last=(i==len(exec_rows)-1)) for i,r in enumerate(exec_rows))

    # Funnel
    funnel_levels = [
        ("Gecrawlt (gesamt)",      total,             100.0,                    C_BLACK),
        ("Lebendig (2xx)",         m["alive"],         pct(m["alive"],total),    "#444444"),
        ("Indexierbar",            indexable,          pct(indexable,total),     "#666666"),
        ("GSC-sichtbar (>0 Impr.)",m["with_imp"],      pct(m["with_imp"],total), "#888888"),
        ("Relevant (&ge;10 Klicks)",m["relevant"],     pct(m["relevant"],total), C_INK40),
    ]
    funnel_svg = svg_funnel(funnel_levels)

    # Q*
    q_segs  = [(name,m["q_dist"].get(name,0),color) for name,_,_,_,color in Q_TIERS]
    q_total = sum(s[1] for s in q_segs)
    q_bar   = svg_stacked_bar(q_segs, q_total)
    q_cards = ""
    for name,subtitle,lo,hi,color in Q_TIERS:
        count = m["q_dist"].get(name,0)
        q_cards += (f'<div class="pillar-card" style="background:{C_GREY};border:0;">'
                    f'<div class="tag" style="color:{color};">{name}</div>'
                    f'<h3>{fmt(count)}</h3>'
                    f'<p>{subtitle}<br/>{pct(count,q_total):.1f}% der Seiten</p></div>')

    # Cluster table
    def cluster_row(c):
        rec_color,rec_bg = {
            "FEHLER":   (C_RED,"#fff5f5"),"DEINDEX":(C_RED,"#fff5f5"),
            "OPTIMIEREN":(C_ORANGE,"#fff8f0"),"CTR":(C_ORANGE,"#fff8f0"),
            "STARK":    (C_GREEN,"#f0fdf4"),"MONITOR":(C_INK40,C_GREY),
        }.get(c["rec"][0],(C_INK40,C_GREY))
        thin_str = f'{c["thin_pct"]:.0f}%' if c["thin_pct"] is not None else "-"
        pos_str  = f'{c["avg_position"]:.1f}' if c["avg_position"]>0 else "-"
        ni_str   = fmt(c["not_indexed"]) if c["not_indexed"]>0 else "-"
        return (f'<tr style="border-bottom:1px solid {C_INK15};">'
                f'<td style="padding:7px 10px;font-weight:600;font-size:17px;">{c["name"]}</td>'
                f'<td style="padding:7px 10px;text-align:right;font-size:17px;">{fmt(c["total"])}</td>'
                f'<td style="padding:7px 10px;text-align:right;font-size:17px;">{fmt(c["indexable"])}</td>'
                f'<td style="padding:7px 10px;text-align:right;font-size:17px;">{fmt(c["impressions"])}</td>'
                f'<td style="padding:7px 10px;text-align:right;font-size:17px;">{pos_str}</td>'
                f'<td style="padding:7px 10px;text-align:right;font-size:17px;">{thin_str}</td>'
                f'<td style="padding:7px 10px;text-align:right;font-size:17px;color:{C_RED if c["not_indexed"]>0 else C_INK40};">{ni_str}</td>'
                f'<td style="padding:7px 10px;text-align:center;">'
                f'<span style="font-size:11px;font-weight:700;background:{rec_bg};color:{rec_color};'
                f'padding:3px 8px;border-radius:3px;letter-spacing:0.06em;text-transform:uppercase;">'
                f'{c["rec"][0]}</span></td></tr>')

    cluster_rows_html = "".join(cluster_row(c) for c in m["clusters"])

    def di_row(c,last=False):
        ni = f', {fmt(c["not_indexed"])} von GSC nicht indexiert' if c["not_indexed"]>0 else ""
        thin_str = f', {c["thin_pct"]:.0f}% duenner Content' if c["thin_pct"] is not None else ""
        return find_row(C_RED,c["name"],
            f'{fmt(c["indexable"])} indexierbare Seiten, {fmt(c["impressions"])} Impressionen{ni}{thin_str}. Kein messbarer Beitrag.',
            "Deindex","gap",last=last)

    def opt_row(c,last=False):
        tp = f'{c["thin_pct"]:.0f}% duenner Content, ' if c["thin_pct"] is not None else ""
        ctr_note = f'{c["ctr_issues"]} Seiten mit CTR-Gap, ' if c["ctr_issues"]>0 else ""
        return find_row(C_ORANGE,c["name"],
            f'{fmt(c["impressions"])} Impressionen, Durchschnitt Position {c["avg_position"]:.1f}. {tp}{ctr_note}Optimierung kann Rankings deutlich heben.',
            "Optimieren","warn",last=last)

    di_html  = "".join(di_row(c,last=(i==len(m["deindex_clusters"])-1))  for i,c in enumerate(m["deindex_clusters"]))  if m["deindex_clusters"]  else find_row(C_GREEN,"Keine eindeutigen Deindex-Kandidaten","Alle Cluster haben Sichtbarkeit oder sind zu klein.","OK","ok",last=True)
    opt_html = "".join(opt_row(c,last=(i==len(m["optimize_clusters"])-1)) for i,c in enumerate(m["optimize_clusters"])) if m["optimize_clusters"] else find_row(C_GREEN,"Keine eindeutigen Optimierungs-Cluster","Seiten sind gut optimiert oder Datenbasis zu klein.","OK","ok",last=True)

    # Error clusters
    err_cluster_html = ""
    err_clusters = [(c["name"],c["error_pct"],c["total"]) for c in m["clusters"] if c["error_pct"]>20][:5]
    if err_clusters:
        err_cluster_html = f'<div style="margin-top:18px;display:flex;gap:12px;flex-wrap:wrap;">'
        for cname,ep,ct in err_clusters:
            err_cluster_html += (f'<div style="padding:10px 16px;background:{C_GREY};border-left:3px solid {C_RED};border-radius:0 4px 4px 0;">'
                                 f'<div style="font-size:15px;font-weight:700;color:{C_BLACK};">{cname}</div>'
                                 f'<div style="font-size:13px;color:{C_INK60};">{ep:.0f}% Fehler ({fmt(ct)} Seiten)</div></div>')
        err_cluster_html += "</div>"

    # ── Assemble slides ──────────────────────────────────────────────────────
    S = []

    # 01 Cover
    S.append(f'''  <section data-screen-label="01 Cover" class="s-cover frame-flush">
    <div class="cover-grid" style="grid-template-rows:auto 1fr auto;">
      <div style="grid-column:1/3;grid-row:1;display:flex;align-items:flex-start;">
        <img src="https://www.more-fire.com/wp-content/uploads/2020/09/morefire-logo-white.svg" alt="more-fire" style="height:56px;"/>
      </div>
      <div style="grid-column:1/3;grid-row:2;align-self:center;">
        <div style="font-size:26px;color:rgba(255,255,255,.78);font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:36px;">{brand.upper()} | SEO-POTENZIALANALYSE</div>
        <h1 class="display" style="color:#fff;max-width:18ch;">Was wirkt. Was bremst. Was jetzt zaehlt.</h1>
        <p style="font-size:36px;color:rgba(255,255,255,.85);font-weight:300;line-height:1.3;margin:40px 0 0;max-width:56ch;">
          Basis: ScreamingFrog Crawl + Google Search Console &middot; {crawl_date}
        </p>
      </div>
    </div>
  </section>''')

    # 02 Executive Summary
    S.append(f'''  <section data-screen-label="02 Executive Summary" class="frame">
    <div class="eyebrow">EXECUTIVE SUMMARY</div>
    <h1 class="title">Die wichtigsten Befunde</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">{domain} &middot; {fmt(total)} gecrawlte Seiten &middot; {fmt(m["with_imp"])} mit GSC-Sichtbarkeit</p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">{exec_html}</div>
    {footer(brand,domain)}
  </section>''')

    # 03 Seiten-Inventar
    S.append(f'''  <section data-screen-label="03 Seiten-Inventar" class="frame">
    <div class="eyebrow">SEITEN-INVENTAR</div>
    <h1 class="title">Wie viel davon ist wirklich relevant?</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Von {fmt(total)} gecrawlten Seiten sind nur {fmt(m["relevant"])} ({pct(m["relevant"],total):.1f}%) traffic-relevant.
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:56px;">{funnel_svg}</div>
    {footer(brand,domain)}
  </section>''')

    # 04 Harte Fehler
    err_rows = []
    if m["err_4xx"]>0:
        err_rows.append(find_row(C_RED,f'4xx-Fehler: {fmt(m["err_4xx"])} Seiten ({pct(m["err_4xx"],total):.1f}%)',
            'Nicht erreichbare Seiten ohne Redirect. Verlust von internem Link-Equity und Crawl-Budget.',"Fix","gap"))
    if m["err_5xx"]>0:
        err_rows.append(find_row(C_RED,f'5xx-Fehler: {fmt(m["err_5xx"])} Seiten ({pct(m["err_5xx"],total):.1f}%)',
            'Server-seitige Fehler. Direkte Beeintraechtigung von Indexierung und Rankings.',"Fix","gap"))
    if m["redir"]>0:
        err_rows.append(find_row(C_ORANGE,f'Weiterleitungen: {fmt(m["redir"])} Seiten ({pct(m["redir"],total):.1f}%)',
            'Redirect-Chains erhoehen Ladezeiten und beeintraechtigen PageRank-Weitergabe. Auf direkte Ziel-URLs auflösen.',"Review","warn"))
    if not err_rows:
        err_rows.append(find_row(C_GREEN,"Keine harten Fehler","Alle Seiten antworten korrekt.","OK","ok"))
    err_rows[-1] = find_row(*[x for x in [err_rows[-1]]][0].split("</div>")) if False else err_rows[-1]  # noop, already built

    S.append(f'''  <section data-screen-label="04 Harte Fehler" class="frame">
    <div class="eyebrow">HARTE FEHLER + WEITERLEITUNGEN</div>
    <h1 class="title">4xx, 5xx und Redirect-Chains</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      {fmt(m["err_4xx"]+m["err_5xx"])} Fehler-Seiten ({pct(m["err_4xx"]+m["err_5xx"],total):.1f}%) und {fmt(m["redir"])} Weiterleitungen im Crawl.
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:56px;">
      {"".join(err_rows)}{err_cluster_html}
    </div>
    {footer(brand,domain)}
  </section>''')

    # 05 Technische Struktur (NEW)
    tech_rows = []
    # Canonical
    if m["has_canonical_data"]:
        ext_pct = pct(m["canon_external"],indexable)
        mis_pct = pct(m["canon_missing"],indexable)
        if m["canon_external"]>0:
            tech_rows.append(find_row(C_ORANGE,
                f'Canonical auf andere URL: {fmt(m["canon_external"])} Seiten ({ext_pct:.1f}%)',
                f'Indexierbare Seiten mit Canonical der auf eine andere URL zeigt. Google soll diese Seite ignorieren, '
                f'aber SF wertet sie als indexierbar. Kann Crawl-Budget verschwenden.', "Review","warn"))
        if m["canon_missing"]>10:
            tech_rows.append(find_row(C_ORANGE,
                f'Kein Canonical-Tag: {fmt(m["canon_missing"])} Seiten ({mis_pct:.1f}%)',
                'Seiten ohne Canonical sind anfaellig fuer unbeabsichtigte Duplizierung. '
                'Mindestens Self-Canonical auf allen indexierbaren Seiten empfohlen.',"Review","warn"))
        if m["canon_self"]>0:
            tech_rows.append(find_row(C_GREEN,
                f'Korrekte Self-Canonicals: {fmt(m["canon_self"])} Seiten ({pct(m["canon_self"],indexable):.1f}%)',
                'Diese Seiten haben einen Canonical der auf sich selbst zeigt.', "OK","ok"))
    else:
        tech_rows.append(find_row(C_INK40,
            "Canonical-Daten nicht im Export enthalten",
            'ScreamingFrog → Configuration → Spider → Extraction → Canonical Link Element aktivieren.',"–","warn"))

    # Crawl depth
    if m["has_depth_data"]:
        deep_pct = pct(m["deep_pages"],indexable)
        col = C_RED if deep_pct>20 else C_ORANGE if deep_pct>10 else C_GREEN
        pill = "gap" if deep_pct>20 else "warn" if deep_pct>10 else "ok"
        tech_rows.append(find_row(col,
            f'Crawltiefe 5+: {fmt(m["deep_pages"])} Seiten ({deep_pct:.1f}%)',
            f'Tiefe: {fmt(m["depth_dist"]["1-2"])} Seiten auf Ebene 1-2, '
            f'{fmt(m["depth_dist"]["3-4"])} auf 3-4, '
            f'{fmt(m["deep_pages"])} auf 5+. Seiten tief im Seitenbaum werden seltener gecrawlt und schlechter gewichtet.',
            "Fix" if deep_pct>20 else "Review",pill))
    else:
        tech_rows.append(find_row(C_INK40,"Crawltiefe-Daten nicht im Export",
            'ScreamingFrog → Bulk Export → Internal → All enthält Crawl Depth.',"–","warn"))

    # Orphans
    if m["has_inlinks_data"] and m["orphan_pages"]>0:
        tech_rows.append(find_row(C_ORANGE,
            f'Verwaiste Seiten (0 interne Inlinks): {fmt(m["orphan_pages"])} Seiten',
            'Indexierbare Seiten ohne interne Verlinkung werden von Google kaum entdeckt und bewertet.',
            "Review","warn",last=True))
    elif tech_rows:
        # Make last row borderless
        pass

    if not tech_rows:
        tech_rows.append(find_row(C_GREEN,"Technische Struktur ohne Auffaelligkeiten","Canonical, Crawltiefe und Verlinkung im gruenen Bereich.","OK","ok",last=True))

    S.append(f'''  <section data-screen-label="05 Technische Struktur" class="frame">
    <div class="eyebrow">TECHNISCHE STRUKTUR</div>
    <h1 class="title">Canonical, Crawltiefe und interne Verlinkung</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Strukturelle Signale die bestimmen, ob Google Seiten richtig findet, bewertet und zuordnet.
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:56px;">
      {"".join(tech_rows)}
    </div>
    {footer(brand,domain)}
  </section>''')

    # 06 On-Page-Hygiene
    hyg_rows = [
        find_row(C_RED if m["missing_title"]>5 else C_ORANGE,
                 f'Fehlende Seitentitel: {fmt(m["missing_title"])} ({pct(m["missing_title"],indexable):.1f}%)',
                 'Fehlende Titles sind direkte Ranking-Verluste. Google generiert schlechten Ersatz.',
                 "Fix" if m["missing_title"]>5 else "Review","gap" if m["missing_title"]>5 else "warn"),
        find_row(C_ORANGE if m["dup_title"]>0 else C_GREEN,
                 f'Doppelte Seitentitel: {fmt(m["dup_title"])} ({pct(m["dup_title"],indexable):.1f}%)',
                 'Doppelte Titles schwaechen Relevanz-Signale und verursachen Kannibalisierung.',
                 "Review" if m["dup_title"]>0 else "OK","warn" if m["dup_title"]>0 else "ok"),
        find_row(C_RED if m["missing_h1"]>5 else C_ORANGE,
                 f'Fehlende H1: {fmt(m["missing_h1"])} ({pct(m["missing_h1"],indexable):.1f}%)',
                 'Die H1 ist das staerkste On-Page-Signal fuer das Haupt-Keyword der Seite.',
                 "Fix" if m["missing_h1"]>5 else "Review","gap" if m["missing_h1"]>5 else "warn"),
        find_row(C_ORANGE if m["multi_h1"]>0 else C_GREEN,
                 f'Mehrfache H1: {fmt(m["multi_h1"])} ({pct(m["multi_h1"],indexable):.1f}%)',
                 'Mehrere H1-Elemente verwaessern das Haupt-Signal und zeigen Markup-Probleme an.',
                 "Review" if m["multi_h1"]>0 else "OK","warn" if m["multi_h1"]>0 else "ok",last=True),
    ]
    S.append(f'''  <section data-screen-label="06 On-Page-Hygiene" class="frame">
    <div class="eyebrow">ON-PAGE-HYGIENE</div>
    <h1 class="title">Titel und H1-Ueberschriften</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Basis: {fmt(indexable)} indexierbare Seiten. {fmt(m["hygiene_issues"])} ({pct(m["hygiene_issues"],indexable):.1f}%) mit mindestens einem behebbaren Problem.
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:56px;">
      {"".join(hyg_rows)}
    </div>
    {footer(brand,domain)}
  </section>''')

    # 07 Q*
    if m["has_wc"]:
        thin_note = (f'{fmt(m["thin_without_imp"])} dunnne Seiten ({pct(m["thin_without_imp"],max(m["total_thin"],1)):.0f}%) '
                     f'haben auch keine GSC-Impressionen: primaere Deindex-Kandidaten.')
        q_content = (f'<div class="cols-4" style="margin-top:20px;">{q_cards}</div>'
                     f'<div style="margin-top:16px;">'
                     f'<div style="font-size:17px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:{C_INK40};margin-bottom:8px;">VERTEILUNG NACH WORTANZAHL</div>'
                     f'{q_bar}</div>'
                     f'<div style="margin-top:12px;padding:13px 18px;background:{C_GREY};border-left:3px solid {C_ORANGE};">'
                     f'<div style="font-size:16px;font-weight:700;color:{C_BLACK};margin-bottom:4px;">Thin Content x Sichtbarkeit</div>'
                     f'<div style="font-size:16px;color:{C_INK60};line-height:1.45;">'
                     f'{fmt(m["thin_with_imp"])} duenne Seiten haben Impressionen (optimieren). {thin_note}'
                     f'</div></div>')
    else:
        q_content = (f'<div style="padding:28px;background:{C_GREY};text-align:center;">'
                     f'<p style="font-size:22px;color:{C_INK60};margin:0;">Word Count nicht im Crawl erfasst.<br/>'
                     f'ScreamingFrog: Configuration &rarr; Spider &rarr; Extraction &rarr; Store Text aktivieren.</p></div>')

    S.append(f'''  <section data-screen-label="07 Content-Qualitaet Q*" class="frame">
    <div class="eyebrow">CONTENT-QUALITAET (Q*)</div>
    <h1 class="title">Wie viel Inhalt haben die Seiten wirklich?</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Basis: {fmt(m["wc_pages"])} Seiten mit Wortanzahl-Daten. Unter 300 Woerter gilt als Optimierungs- oder Deindex-Kandidat.
    </p>
    <div style="flex:1;padding-bottom:60px;">{q_content}</div>
    {footer(brand,domain)}
  </section>''')

    # 08 GSC Indexierungsstatus (NEW — only if coverage data available)
    if m["has_coverage"]:
        cov_rows = []
        if m["crawled_not_indexed"]>0:
            cov_rows.append(find_row(C_RED,
                f'Gecrawlt – nicht indexiert: {fmt(m["crawled_not_indexed"])} Seiten',
                'Google hat diese Seiten gecrawlt, aber bewusst NICHT indexiert. Kein technisches Problem. '
                'Content-Qualitaetssignal: duenner Inhalt, geringe Originalitaet oder zu geringe Relevanz '
                'aus Googles Sicht. Staerkste Empfehlung: Inhalt grundlegend ueberarbeiten oder deindexieren.',
                "Fix","gap"))
        if m["discovered_not_indexed"]>0:
            cov_rows.append(find_row(C_RED,
                f'Gefunden – nicht indexiert: {fmt(m["discovered_not_indexed"])} Seiten',
                'Google hat diese Seiten entdeckt (z.B. ueber interne Links), aber noch nicht gecrawlt. '
                'Crawl-Budget wird nicht auf diese Seiten verwendet. Tiefe Seiten mit schwacher interner Verlinkung.',
                "Review","warn"))
        if m["soft_404"]>0:
            cov_rows.append(find_row(C_RED,
                f'Soft-404: {fmt(m["soft_404"])} Seiten',
                'Seiten antworten mit HTTP 200, sehen fuer Google aber aus wie leere oder nicht-existente Seiten. '
                'Haeufig: tag-Seiten ohne Inhalt, leere Suchergebnisse, Platzhalter-Seiten.',
                "Fix","gap"))
        if m["dup_no_canonical"]>0:
            cov_rows.append(find_row(C_ORANGE,
                f'Duplikat ohne Nutzer-Canonical: {fmt(m["dup_no_canonical"])} Seiten',
                'Google erkennt diese Seiten als Duplikat, aber kein Canonical wurde gesetzt oder Google stimmt '
                'dem gesetzten Canonical nicht zu. Google waehlt selbst das kanonische Element.',
                "Review","warn"))
        if not cov_rows:
            cov_rows.append(find_row(C_GREEN,"Keine kritischen Indexierungsprobleme",
                "Alle gecrawlten Seiten werden indexiert oder sind bewusst ausgeschlossen.","OK","ok"))

        S.append(f'''  <section data-screen-label="08 GSC Indexierungsstatus" class="frame">
    <div class="eyebrow">GSC INDEXIERUNGSSTATUS</div>
    <h1 class="title">Warum indexiert Google bestimmte Seiten nicht?</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Aus dem GSC Index-Coverage-Report. Unterschied: technisch ausgeschlossen (bewusst) vs. inhaltlich abgelehnt (Problem).
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:80px;">
      {"".join(cov_rows)}
    </div>
    <div class="context-note">
      <svg width="20" height="20" viewBox="0 0 22 22" fill="none" style="flex-shrink:0;color:{C_RED};">
        <circle cx="11" cy="11" r="10" stroke="currentColor" stroke-width="1.5"/>
        <path d="M11 10v6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="11" cy="7" r="1" fill="currentColor"/>
      </svg>
      <span class="context-label">Wichtig</span>
      <span class="context-text">"Gecrawlt – nicht indexiert" ist ein Content-Qualitaetssignal, kein technisches Problem. Technische Fixes helfen hier nicht.</span>
    </div>
    {footer(brand,domain)}
  </section>''')
    else:
        # Placeholder slide if no coverage data
        S.append(f'''  <section data-screen-label="08 GSC Indexierungsstatus" class="frame">
    <div class="eyebrow">GSC INDEXIERUNGSSTATUS</div>
    <h1 class="title">Index-Coverage-Daten nicht geladen</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">Fuer diese Analyse bitte GSC &rarr; Index &rarr; Coverage &rarr; Export als CSV und mit --gsc-coverage uebergeben.</p>
    <div style="flex:1;display:flex;align-items:center;justify-content:center;">
      <div style="padding:32px;background:{C_GREY};text-align:center;max-width:800px;">
        <div style="font-size:22px;font-weight:700;color:{C_BLACK};margin-bottom:12px;">Warum ist dieser Report wichtig?</div>
        <div style="font-size:20px;color:{C_INK60};line-height:1.5;">
          "Gecrawlt – nicht indexiert" zeigt, wo Google Inhalte aktiv ablehnt, obwohl sie technisch erreichbar sind.
          Das ist das staerkste Content-Qualitaetssignal das GSC liefert – und wird haeufig uebersehen.
        </div>
      </div>
    </div>
    {footer(brand,domain)}
  </section>''')

    # 09 CTR-Potenzial (NEW)
    ctr_rows = []
    if m["ctr_opportunities"]:
        # Group by cluster
        for cname, cd in m["ctr_by_cluster"][:5]:
            ctr_rows.append(find_row(C_ORANGE,
                f'{cname} — {cd["count"]} Seiten unter CTR-Benchmark',
                f'{fmt(cd["impressions"])} Impressionen in diesem Cluster mit ungewoehnlich niedriger Klickrate. '
                f'Ursache: Title und/oder Meta Description sprechen Suchintention nicht klar genug an.',
                "Review","warn"))
    if m["top_low_hanging_queries"]:
        q_list = ", ".join(f'"{q["query"]}" (Pos. {q["position"]:.1f})' for q in m["top_low_hanging_queries"][:4])
        ctr_rows.append(find_row(C_ORANGE,
            f'Low-Hanging-Fruit Keywords: {len(m["top_low_hanging_queries"])} Queries auf Position 4-10 mit &ge;50 Impressionen',
            f'Beispiele: {q_list}. Kleine Ranking-Verbesserung = ueberproportional mehr Klicks.',
            "Potenzial","warn"))
    if not ctr_rows:
        ctr_rows.append(find_row(C_GREEN,"Keine signifikanten CTR-Gaps identifiziert",
            "Alle gut positionierten Seiten haben eine Klickrate im erwarteten Bereich.","OK","ok"))

    # CTR table of top opportunities
    ctr_table_rows = ""
    for item in m["ctr_opportunities"][:8]:
        ctr_pct_str = f'{item["ctr"]*100:.1f}%'
        bench_str   = f'{item["benchmark"]*100:.0f}%'
        ctr_table_rows += (f'<tr style="border-bottom:1px solid {C_INK15};">'
                           f'<td style="padding:6px 10px;font-size:16px;color:{C_INK60};">{item["url"][:60]}{"..." if len(item["url"])>60 else ""}</td>'
                           f'<td style="padding:6px 10px;text-align:right;font-size:16px;">{item["position"]:.1f}</td>'
                           f'<td style="padding:6px 10px;text-align:right;font-size:16px;">{fmt(item["impressions"])}</td>'
                           f'<td style="padding:6px 10px;text-align:right;font-size:16px;color:{C_RED};font-weight:700;">{ctr_pct_str}</td>'
                           f'<td style="padding:6px 10px;text-align:right;font-size:16px;color:{C_INK40};">{bench_str}</td></tr>')

    ctr_table_html = ""
    if ctr_table_rows:
        ctr_table_html = (f'<div style="margin-top:20px;">'
                          f'<div style="font-size:16px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:{C_INK40};margin-bottom:8px;">TOP CTR-GAPS (IST vs. BENCHMARK)</div>'
                          f'<table style="width:100%;border-collapse:collapse;font-size:16px;">'
                          f'<tr style="background:{C_BLACK};color:#fff;">'
                          f'<th style="padding:7px 10px;text-align:left;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">URL</th>'
                          f'<th style="padding:7px 10px;text-align:right;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Position</th>'
                          f'<th style="padding:7px 10px;text-align:right;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Impressionen</th>'
                          f'<th style="padding:7px 10px;text-align:right;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;color:{C_ORANGE};">Ist-CTR</th>'
                          f'<th style="padding:7px 10px;text-align:right;font-size:13px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Benchmark</th>'
                          f'</tr>{ctr_table_rows}</table></div>')

    S.append(f'''  <section data-screen-label="09 CTR-Potenzial" class="frame">
    <div class="eyebrow">CTR-OPTIMIERUNGSPOTENZIAL</div>
    <h1 class="title">Gut positioniert, zu wenig geklickt</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Seiten in den Top 10 mit CTR deutlich unter Benchmark. Ursache: Title und Meta Description passen nicht zur Suchintention.
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:flex-start;padding-top:16px;padding-bottom:56px;">
      {"".join(ctr_rows)}{ctr_table_html}
    </div>
    {footer(brand,domain)}
  </section>''')

    # 10 Section Divider
    S.append(f'''  <section data-screen-label="10 Section Empfehlungen" class="s-section frame-flush"
           style="display:flex;align-items:center;justify-content:flex-start;padding:0 var(--pad-x);">
    <div style="display:grid;grid-template-columns:auto 1fr;gap:80px;align-items:center;width:100%;">
      <div class="bignum" style="color:{C_RED};">02</div>
      <div>
        <div style="font-size:24px;color:{C_ORANGE};font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:24px;">ZWEITER TEIL</div>
        <h1 class="display" style="color:#fff;font-size:120px;max-width:14ch;">Prioritaeten.</h1>
        <p style="font-size:30px;color:rgba(255,255,255,.7);font-weight:300;line-height:1.35;margin:32px 0 0;max-width:44ch;">
          Welche Cluster deindexieren, welche optimieren, welche in Ruhe lassen.
        </p>
      </div>
    </div>
    {footer_white(brand,domain)}
  </section>''')

    # 11 Cluster Analysis
    S.append(f'''  <section data-screen-label="11 Cluster-Analyse" class="frame">
    <div class="eyebrow">CLUSTER-ANALYSE</div>
    <h1 class="title">Alle Bereiche auf einen Blick</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">Gruppierung nach erstem URL-Verzeichnissegment. Nicht indexiert = GSC Coverage Daten (falls geladen).</p>
    <div style="margin-top:12px;overflow:hidden;flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:56px;">
      <table style="width:100%;border-collapse:collapse;font-size:17px;">
        <thead>
          <tr style="background:{C_BLACK};color:#fff;">
            <th style="padding:8px 10px;text-align:left;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;width:20%;">Cluster</th>
            <th style="padding:8px 10px;text-align:right;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Gesamt</th>
            <th style="padding:8px 10px;text-align:right;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Indexierbar</th>
            <th style="padding:8px 10px;text-align:right;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Impressionen</th>
            <th style="padding:8px 10px;text-align:right;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Ø Pos.</th>
            <th style="padding:8px 10px;text-align:right;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Duenn</th>
            <th style="padding:8px 10px;text-align:right;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;color:{C_ORANGE};">Nicht idx.</th>
            <th style="padding:8px 10px;text-align:center;font-size:12px;letter-spacing:0.06em;text-transform:uppercase;font-weight:700;">Empfehlung</th>
          </tr>
        </thead>
        <tbody>{cluster_rows_html}</tbody>
      </table>
    </div>
    {footer(brand,domain)}
  </section>''')

    # 12 Deindex
    S.append(f'''  <section data-screen-label="12 Deindex-Kandidaten" class="frame">
    <div class="eyebrow">DEINDEX-EMPFEHLUNGEN</div>
    <h1 class="title">Ballast aus dem Index entfernen</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Cluster mit vielen indexierten Seiten ohne messbare Sichtbarkeit. Deindexierung schont Crawl-Budget und verbessert Index-Qualitaet.
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:80px;">{di_html}</div>
    <div class="context-note">
      <svg width="20" height="20" viewBox="0 0 22 22" fill="none" style="flex-shrink:0;color:{C_RED};">
        <circle cx="11" cy="11" r="10" stroke="currentColor" stroke-width="1.5"/>
        <path d="M11 10v6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="11" cy="7" r="1" fill="currentColor"/>
      </svg>
      <span class="context-label">Hinweis</span>
      <span class="context-text">Deindex-Entscheidungen immer auf URL-Ebene verifizieren, bevor noindex gesetzt wird.</span>
    </div>
    {footer(brand,domain)}
  </section>''')

    # 13 Optimize
    S.append(f'''  <section data-screen-label="13 Optimierungs-Prioritaeten" class="frame">
    <div class="eyebrow">OPTIMIERUNGSPRIORITAETEN</div>
    <h1 class="title">Schlafende Riesen wecken</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Cluster mit Sichtbarkeit, aber suboptimalen Rankings, dunnem Content oder CTR-Gaps. Traffic-Steigerung ohne neue Seiten moeglich.
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:56px;">{opt_html}</div>
    {footer(brand,domain)}
  </section>''')

    # 14 Hreflang (optional)
    if m["has_hreflang"]:
        hl = m["hreflang_data"]
        total_hl = hl.get("total",0)
        issues   = hl.get("issues",{})
        n_issues = sum(issues.values())
        hl_rows  = []
        if n_issues>0:
            for issue_name,count in sorted(issues.items(),key=lambda x:-x[1])[:5]:
                hl_rows.append(find_row(C_RED,
                    f'{issue_name}: {fmt(count)} Faelle',
                    'Hreflang-Fehler verhindern korrekte Sprachzuweisung und koennen Duplicate-Content-Signale erzeugen.',
                    "Fix","gap"))
        else:
            hl_rows.append(find_row(C_GREEN,f'Keine Hreflang-Fehler in {fmt(total_hl)} analysierten Eintraegen',
                'Alle Hreflang-Annotationen sind korrekt.', "OK","ok",last=True))

        S.append(f'''  <section data-screen-label="14 Hreflang" class="frame">
    <div class="eyebrow">HREFLANG-ANALYSE</div>
    <h1 class="title">Mehrsprachige Seitenstruktur</h1>
    <p class="lead" style="margin-top:4px;color:{C_INK60};">
      Basis: {fmt(total_hl)} Hreflang-Eintraege aus ScreamingFrog. {fmt(n_issues)} Eintraege mit Problemen ({pct(n_issues,total_hl):.1f}%).
    </p>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:56px;">
      {"".join(hl_rows)}
    </div>
    {footer(brand,domain)}
  </section>''')

    # Closing
    S.append(f'''  <section data-screen-label="{'15' if m['has_hreflang'] else '14'} Closing" class="s-grey frame frame-centered">
    <div class="frame-header">
      <div class="eyebrow">Naechste Schritte</div>
      <h1 class="title">Was jetzt.</h1>
    </div>
    <div class="frame-body">
      <div style="width:100%;display:flex;flex-direction:column;gap:48px;">
        <p class="lead" style="color:{C_INK60};max-width:52ch;margin:0;">
          Diese Analyse zeigt Muster, keine Einzelfehler. Die groessten Hebel liegen in der Reduktion
          von Ballast-Seiten, der Behebung von Crawl-Problemen und der gezielten Optimierung
          der Cluster mit ungenutztem Potenzial.
        </p>
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:48px;">
          <div>
            <div style="font-size:24px;color:{C_RED};font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:14px;">Kontakt</div>
            <div style="font-size:28px;font-weight:600;color:{C_BLACK};line-height:1.25;letter-spacing:-0.01em;">
              Martin Weber<br/><span style="color:{C_INK60};font-weight:400;font-size:22px;">morefire GmbH, K&ouml;ln</span>
            </div>
          </div>
          <div>
            <div style="font-size:24px;color:{C_RED};font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:14px;">E-Mail</div>
            <div style="font-size:28px;font-weight:600;color:{C_BLACK};letter-spacing:-0.01em;">m.weber@more-fire.com</div>
          </div>
        </div>
      </div>
    </div>
    <div class="footer">
      <span>{brand} | SEO-Potenzialanalyse &middot; {domain}</span>
      <img class="logo" src="https://www.more-fire.com/wp-content/uploads/2020/09/morefire-logo-farbig.svg" alt="more-fire"/>
    </div>
  </section>''')

    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<title>more-fire &mdash; SEO-Potenzialanalyse &middot; {brand}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="stylesheet" href="./deck-theme.css"/>
</head>
<body>
<script>window.TWEAK_DEFAULTS={{"accent":"#DB3543","secondary":"#f08262","titleSize":72,"bodySize":30,"showLogo":true}};</script>
<deck-stage width="1920" height="1080">
{"".join(S)}
</deck-stage>
<script src="./deck-stage.js"></script>
<script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
<script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>
<script type="text/babel" src="./tweaks-panel.jsx"></script>
<div id="tweaks-root"></div>
<script type="text/babel">
  function TweaksApp(){{
    const [t,setTweak]=useTweaks(window.TWEAK_DEFAULTS);
    React.useEffect(()=>{{
      const r=document.documentElement.style;
      r.setProperty('--c-red',t.accent);r.setProperty('--c-orange',t.secondary);
      r.setProperty('--type-title',t.titleSize+'px');r.setProperty('--type-body',t.bodySize+'px');
    }},[t]);
    return(<TweaksPanel title="Tweaks"><TweakSection label="Colors"/>
      <TweakColor label="Accent" value={{t.accent}} options={{['#DB3543','#1d1d1b','#f08262']}} onChange={{(v)=>setTweak('accent',v)}}/>
      <TweakColor label="Secondary" value={{t.secondary}} options={{['#f08262','#ffd433','#DB3543']}} onChange={{(v)=>setTweak('secondary',v)}}/>
      <TweakSection label="Typography"/>
      <TweakSlider label="Title" value={{t.titleSize}} min={{56}} max={{120}} unit="px" onChange={{(v)=>setTweak('titleSize',v)}}/>
      <TweakSlider label="Body" value={{t.bodySize}} min={{24}} max={{44}} unit="px" onChange={{(v)=>setTweak('bodySize',v)}}/>
    </TweaksPanel>);
  }}
  ReactDOM.createRoot(document.getElementById('tweaks-root')).render(<TweaksApp/>);
</script>
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="SEO Potential Analysis v2")
    p.add_argument("--sf",            required=True)
    p.add_argument("--gsc",           required=True)
    p.add_argument("--brand",         required=True)
    p.add_argument("--domain",        required=True)
    p.add_argument("--output",        required=True)
    p.add_argument("--gsc-coverage",  default=None)
    p.add_argument("--gsc-queries",   default=None)
    p.add_argument("--sf-hreflang",   default=None)
    args = p.parse_args()

    print(f"Lade SF: {args.sf}")
    pages = load_sf(args.sf)
    print(f"  -> {len(pages)} Seiten")

    print(f"Lade GSC Pages: {args.gsc}")
    gsc = load_gsc(args.gsc)
    print(f"  -> {len(gsc)} URLs")

    coverage = None
    if args.gsc_coverage:
        print(f"Lade GSC Coverage: {args.gsc_coverage}")
        coverage = load_gsc_coverage(args.gsc_coverage)
        n = sum(len(v) for v in coverage.values())
        print(f"  -> {n} Coverage-Eintraege")

    queries = None
    if args.gsc_queries:
        print(f"Lade GSC Queries: {args.gsc_queries}")
        queries = load_gsc_queries(args.gsc_queries)
        print(f"  -> {len(queries)} Queries")

    hreflang = None
    if args.sf_hreflang:
        print(f"Lade Hreflang: {args.sf_hreflang}")
        hreflang = load_sf_hreflang(args.sf_hreflang)
        print(f"  -> {hreflang.get('total',0)} Eintraege")

    print("Berechne Metriken...")
    m = compute(pages, gsc, coverage=coverage, queries=queries, hreflang=hreflang)
    if not m:
        print("Fehler: Keine Daten.", file=sys.stderr); sys.exit(1)

    crawl_date = datetime.now().strftime("%B %Y")
    print("Generiere HTML-Deck...")
    html = generate_html(m, args.brand, args.domain, crawl_date)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"\nDeck gespeichert: {out}")
    print(f"Slides: {'15' if m.get('has_hreflang') else '14'} (inkl. {'Hreflang' if m.get('has_hreflang') else 'kein Hreflang'})")

if __name__ == "__main__":
    main()

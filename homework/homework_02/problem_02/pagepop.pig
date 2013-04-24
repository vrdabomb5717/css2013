-- Pig script to calculate incoming page links to each page in Wikipedia.
-- Run using the run_pagepop.sh

-- Load tab-separated articles
edges = LOAD '$INPUT' AS (source_id, source_url, target);

-- Fill in code here to compute page popularity

-- Get page counts for each target link
incoming_links = foreach edges generate target, source_id;
incoming_pages = group incoming_links by target;
page_counts = foreach incoming_pages generate group as page, COUNT(incoming_links) as page_count;
page_counts = foreach page_counts generate CONCAT('http://en.wikipedia.org/wiki/', page) as page, page_count;
-- dump page_counts;

-- Join page counts with page ids to generate output
edges = join edges by source_url, page_counts by page;
edges = foreach edges generate source_id, source_url, page_count;

-- Write tab-separate output
STORE edges INTO '$OUTPUT';
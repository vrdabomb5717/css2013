-- Pig script to count words in wikipedia
-- Run using the run_wordcount.sh

-- Load tab-separated articles
articles = load '$INPUT' USING PigStorage('\t') as (id, url, text);

-- Fill in code here to count words across all article text
articles = foreach articles generate flatten(TOKENIZE(text)) as word;
articles = filter articles by word matches '\\w+';
words = group articles by word;
articles = foreach words generate group as word, COUNT(articles) as word_count;
articles = filter articles by word_count >= 10;

-- Write tab-separate output
store articles into '$OUTPUT';

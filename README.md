# WikiDump Indexer and Search  

## Description  

### Indexer  
Parses the wikipedia dump and creates an inverted index. The parser is done using regex. The indexer creates multiple files, token offset files and titles. Check out [Nikit's repository](https://github.com/Nikit-Uppala/Wikipedia-Search-Engine) for the original parser code.  

The dump used here is the 80GB english wiki dump (compressed xml bz2 file size is around 18GB). The inverted index size is around 17GB (when the uncompressed file size is 80GB). The time taken for the index creation was around 5 hours.  

This is followed by the merging and secondary inverted index creation which took around 1.5 hours. The `merge.py` code creates a single index file and a single token offset file. The `secinv.py` file creates the secondary inverted indexes for the titles and the token offsets.  

The final index consists of  
- the main inverted index `invind`
- vocabulary `indoff`
- titles `titles`
- titles offsets `titles_off`
- document count `doc_count`
- secondary index of vocabulary `indoff_secinv.json`
- secondary index of titles offsets `titles_off_secinv.json`

You can download the dumps from the following links,  
- [Small dump (compressed size: 40MB)](https://drive.google.com/file/d/1CD1sBLGkxOb7eybNEFc7yF96cP_plJOn/view?usp=sharing)  
- [Big dump (compressed size: 18GB)](https://dumps.wikimedia.org/enwiki/20210720/enwiki-20210720-pages-articles-multistream.xml.bz2)  

To understand the concepts and do your own version follow this link, [Standford Information Retrieval Course](https://nlp.stanford.edu/IR-book/html/htmledition/contents-1.html)  

To install the python dependencies, run the command  
```bash
pip install -r requirements.txt
```  

You can start the indexer using,
```bash
bash index.sh <compressed bz2 dump file path> <target index path>
```  

### Search  
You can search multiple queries as plain query and field query by adding them to a file and send them to `search.py` and the output is stored in the `queries_op.txt`.  
The output for each query is the top 10 results' titles followed by time taken for search.  

You can run the search using,
```bash
bash search.sh <index path> <query file path>
```  

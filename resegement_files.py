#####################
# Use case:
#     The corpus consists of too many small files, and it seems that there are many duplicate documents.
#     This code generates equally sized files (defaults to 300), with duplicates removed.
#     File specefic configurations like domain and seperators are to be used at one's own discretion.
#####################
from collections import defaultdict
import os
import glob
import hashlib


def split_domains(files):
    domain_files = defaultdict(list)
    for f in files:
        domain = f.split('/')[-2]
        domain_files[domain].append(f)
    return domain_files


def reformat_seperators(corpus):
    corpus = corpus.replace("\n\n", "\n")
    return corpus.strip()  # remove empty lines at the end of the file


def remove_duplicate(corpus, hash_set):
    filtered = ""
    session_sep = "\n\n"
    for session in corpus.split(session_sep):
        hash_value = hashlib.md5(session.encode("utf-8")).hexdigest()
        if hash_value in hash_set:
            continue
        else:
            filtered += session + session_sep
            hash_set.add(hash_value)
    return filtered, hash_set


def merge_files(domain, files, out_fpath, file_size_limit=300):

    def write_file(merged_corpus):
        fname = f"{domain}.{file_cnt:04d}.txt"
        fpath = os.path.join(out_fpath, domain, fname)
        with open(fpath, 'w') as f:  # remainder
            f.write(merged_corpus)

    domain_dir = os.path.join(out_fpath, domain)
    if not os.path.exists(domain_dir):
        os.makedirs(domain_dir)
    print(f"processing {domain}... writing to {domain_dir}")

    merged_file_size = 0 # MB
    merged_corpus = ""
    file_cnt = 0
    hash_set = set()
    for f in files:
        merged_corpus += open(f).read()
        merged_file_size += os.path.getsize(f) / (1024 * 1024)  # MB
        if merged_file_size > file_size_limit:
            merged_corpus = reformat_seperators(merged_corpus)
            merged_corpus, hash_set = remove_duplicate(merged_corpus, hash_set)
            write_file(merged_corpus)
            merged_corpus = ""
            merged_file_size = 0
            file_cnt += 1

    # remainder
    merged_corpus = reformat_seperators(merged_corpus)
    merged_corpus, hash_set = remove_duplicate(merged_corpus, hash_set)
    write_file(merged_corpus)


files = glob.glob("./**/*.txt")
domain_files = split_domains(files)
out_fpath = "dlarva_corpus_merged/"
for d, f in domain_files.items():
    merge_files(d, f, out_fpath)

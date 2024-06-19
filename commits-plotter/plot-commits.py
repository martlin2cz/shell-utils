#!/bin/python3.8

from git import Repo
from datetime import datetime
from pandas import pandas
import argparse

def list_commits(repo_path = ".", refs_names=None):
    repo = Repo(repo_path)

    if refs_names is None:
        refs = repo.heads
    else:
        refs = refs_names
    
    commits = set()
    for ref in refs:
        for commit in repo.iter_commits(ref):
            commits.add(commit)

    return commits

def plot_commits(commits, tui):
    dataset = to_dataset(commits)
    draw_the_graph(dataset, tui)

def draw_the_graph(dataset, tui):
    import matplotlib
    if tui:
        matplotlib.use('module://drawilleplot')

    from matplotlib import pyplot
    import matplotlib.dates

    pyplot.figure()
    pyplot.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%Y'))
    pyplot.gca().xaxis.set_major_locator(matplotlib.dates.MonthLocator())

    pyplot.gca().yaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    pyplot.gca().yaxis.set_major_locator(matplotlib.dates.HourLocator())

    pyplot.gcf().autofmt_xdate()

    pyplot.scatter(dataset.keys(), dataset.values())
    pyplot.show()
#    pyplot.close()

def to_dataset(commits):
    return dict([ [ commit_date(commit), commit_time(commit) ] for commit in commits ])

def commit_date(commit):
    return datetime.date(commit.committed_datetime)

def commit_time(commit):
    base_date = datetime.now().date()
    time = datetime.time(commit.committed_datetime) 
    return datetime.combine(base_date, time)

def doit(repo_path, refs_names, tui):
    commits = list_commits(repo_path, refs_names)
    plot_commits(commits, tui)


parser = argparse.ArgumentParser(
        description="The tool for outputting the GIT commits in that date-time chart. Version 1.0")

parser.add_argument("-refs", type=str, nargs="*", metavar="refs_names",
        help = "The refs, like commit id, branch or tag name, can specify multiple of them")

parser.add_argument("-tui", action="store_true",
        help = "If set, outputs the graph in the ascii-art like text graph (graphical window otherwise)")

parser.add_argument("repo_path", type=str, metavar="repo_path", nargs="?", default=".",
        help = "The path to the repo, defaults to the current directory")

args = parser.parse_args()
doit(args.repo_path, args.refs, args.tui)




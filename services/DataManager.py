import os
import json
import time
import random
import pandas as pd
import numpy as np

from collections import defaultdict
from collections import Counter

from services.Stats import Stats
from services.OMDB import OMDB

_DATA_DIR = os.getcwd() + '/data/'
_TITLES_FILE = _DATA_DIR + 'movie_titles.txt'
_MOVIE_DATA_DIR = _DATA_DIR + 'movie_data/'
_CACHE_DIR = _DATA_DIR + 'cache/'

OMDB = OMDB()


class DataManager:
    """
        The DataManager provides all utility functions that can be used
        throughout the website. The DataManager serves as a central class
        which hosts all the functions in one place.

        Please note: the content has been limited to the first 69 movies.
        This was done to speed up the initialization time, this way you don't
        have to wait a long time for all data to be initialized. You are free
        to remove this barrier.
     """

    ratings = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    titles = {}

    def __init__(self, init=False):
        """
            Initialize the DataManager.

            If init is set to False, the data will be loaded from cache. The
            init parameter should only be set to True on server startup.
        """
        if init \
            or not (os.path.isfile(_DATA_DIR + 'ratings.json') and
                    os.path.isfile(_DATA_DIR + 'matrix.csv')):
            self.initialize_data()

            if not os.path.isdir(_CACHE_DIR):
                os.mkdir(_CACHE_DIR)
        else:
            self.load_snapshot()

        with open(_TITLES_FILE, encoding="ISO-8859-1") as f:
            for line in f:
                split = line.strip().split(',')
                entry = {
                    'Release-Year': split[1],
                    'Title': split[2],
                    'Id': int(split[0])
                }
                self.titles[int(split[0])] = entry

    def initialize_data(self):
        """
            Initializes the dataset by computing the similarity matrix and ratings per movie.
        """
        movieFiles = os.listdir(_MOVIE_DATA_DIR)[:69]
        ratingCache = defaultdict(dict)

        for f in movieFiles:
            with open(_MOVIE_DATA_DIR + f, encoding="ISO-8859-1") \
                    as movieRatings:
                line = movieRatings.readline()
                movieId = None
                while line:
                    line = line.strip()
                    if line[-1] == ':':
                        movieId = int(line.strip().replace(':', ''))
                        line = movieRatings.readline()

                    data = line.strip().split(',')
                    userId = int(data[0])
                    rating = int(data[1])
                    year = int(data[2].split('-')[0])

                    self.ratings[year][movieId][0] += rating
                    self.ratings[year][movieId][1] += 1
                    ratingCache[userId][movieId] = rating

                    line = movieRatings.readline()

        # Take the average rating per year
        for year in self.ratings:
            for movie in self.ratings[year]:
                rating = self.ratings[year][movie]
                rating = (rating[0] / rating[1], rating[1])

        # Make a matrix
        corr = defaultdict(lambda: defaultdict(lambda: 0))

        for user in ratingCache:
            for movie in ratingCache[user]:
                for otherMovie in ratingCache[user]:
                    if movie == otherMovie:
                        continue
                    corr[otherMovie][movie] += ratingCache[user][movie] - 3

        self.matrix = pd.DataFrame.from_dict(corr).fillna(0)

        # Normalize values
        for col in self.matrix.columns:
            total = sum(self.matrix[col])
            normalized = self.matrix[col] / total
            self.matrix[col] = normalized

        self.save_snapshot()

    def load_snapshot(self):
        """
            Loads data snapshots from file.
        """
        with open(_DATA_DIR + 'ratings.json', 'r') as f:
            self.ratings = json.load(f)

        with open(_DATA_DIR + 'matrix.csv') as f:
            ncols = len(f.readline().split(','))

        data = np.loadtxt(_DATA_DIR + 'matrix.csv',
                          delimiter=',',
                          skiprows=1,
                          usecols=range(1, ncols+1))
        self.matrix = pd.DataFrame(data)

    def save_snapshot(self):
        """
            Save snapshots to file.
        """
        # Save ratings
        if os.path.isfile(_DATA_DIR + 'ratings.json'):
            os.remove(_DATA_DIR + 'ratings.json')
        with open(_DATA_DIR + 'ratings.json', 'w') as f:
            json.dump(self.ratings, f)

        # Save correlation matrix
        if os.path.isfile(_DATA_DIR + 'matrix.csv'):
            os.remove(_DATA_DIR + 'matrix.csv')
        with open(_DATA_DIR + 'matrix.csv', 'w') as f:
            f.write(','.join([str(col) for col in self.matrix.columns]) + '\n')
            for movieId, row in self.matrix.iterrows():
                valStr = ','.join([str(item) for item in row])
                f.write(str(movieId) + ',' + valStr + '\n')

    def get_titles(self):
        """
            Returns the meta data of all movies.
        """
        return self.titles

    def get_ratings(self, movieId):
        """
            Retreive all ratings from a movie.
        """
        ratings = {}
        for year in self.ratings:
            if str(movieId) in self.ratings[year].keys():
                ratings[year] = self.ratings[year][str(movieId)]
        return ratings

    def get_top_correlated(self, movieId, num=5):
        """
            Retreive the top correlated movies for a specified movie.
        """
        row = Counter()
        for i in range(len(self.matrix.columns)):
            other = self.matrix.columns[i]
            if other == movieId:
                continue
            row[other] = self.matrix.loc[movieId][other]
        return [x for (x, _) in row.most_common(num)]

    def get_movie_title(self, movieId):
        """
            Returns the meta data for a specified movie if it exists.
        """
        if movieId in self.titles.keys():
            return self.titles[movieId]
        else:
            return {}

    def _current_time(self):
        """
            Calculate the current timestamp
        """
        current_milli_time = lambda: int(round(time.time() * 1000))
        return current_milli_time()

    def _meta_from_cache(self, movieId):
        """
            Load movie meta from cache.
        """
        with open(_CACHE_DIR + str(movieId) + '.json') as f:
            return json.load(f)

    def _cache_meta(self, movieId):
        """
            Save movie meta to cache.
        """
        meta = self.get_movie_title(movieId)
        omdbMeta = OMDB.get(meta["Title"])
        meta['Poster'] = omdbMeta['Poster']
        meta['Plot'] = omdbMeta['Plot']

        print(self.get_top_correlated(movieId))
        stats = {
                    'Meta': meta,
                    'Ratings': self.get_ratings(movieId),
                    'Correlated': self.get_top_correlated(movieId)
                }
        stats.update({'Time': self._current_time()})

        f = open(_CACHE_DIR + str(stats['Meta']['Id']) + '.json', "w+")
        f.write(json.dumps(stats, indent=4, sort_keys=True))
        f.close()

        return stats

    def get_movie_stats(self, movieId):
        """
            Fetch movie meta and statistics.
        """
        if not os.path.isfile(_CACHE_DIR + str(movieId) + '.json'):
            return self._cache_meta(movieId)

        stats = self._meta_from_cache(movieId)

        # If the cache is older then 1 week, re-cache.
        if (self._current_time() - stats['Time'] >= 604800000):
            stats = self._cache_meta(movieId)

        return stats

    def _top_rated_from_cache(self):
        """
            Load movie meta from cache.
        """
        with open(_CACHE_DIR + 'top-rated.json') as f:
            return json.load(f)

    def _cache_top_rated(self):
        """
            Save top rated rankings to cache.
        """
        print({self.get_titles()[film]['Id']: Stats.computeRatings(self.get_movie_stats(self.get_titles()[film]['Id'])['Ratings'], perYear=False) \
                for film in sorted(self.get_titles())[:69]})

        movies = {
            Stats.computeRatings(self.get_movie_stats(film)['Ratings'], False):
            film for film in sorted(self.get_titles())[:69]
        }

        top = sorted(list(movies.keys())[:69], reverse=True)

        stats = {'Rankings': [movies[movie] for movie in top], 'Time': self._current_time()}

        f = open(_CACHE_DIR + 'top-rated.json', "w+")
        f.write(json.dumps(stats, indent=4, sort_keys=False))
        f.close()

        return stats

    def get_top_rated(self, preLoaded=False, index=0, limit=-1):
        """
            Order all movies by their ratings.
        """
        if not os.path.isfile(_CACHE_DIR + 'top-rated.json'):
            stats = self._cache_top_rated()

        if 'stats' not in locals():
            stats = self._top_rated_from_cache()

            # If the cache is older then 1 week, re-cache.
            if (self._current_time() - stats['Time'] >= 604800000):
                stats = self._cache_top_rated()['Rankings']

        if limit == -1:
            return [stats['Rankings'][i] for i in range(index, len(stats['Rankings']))]

        if (len(stats['Rankings']) < (index + limit)):
            return [stats['Rankings'][i] for i in range(index, len(stats['Rankings']))]

        return [stats['Rankings'][i] for i in range(index, (index + limit))]

    def pick_random_movies(self, amount=10):
        """
            Pick a random amount of films from the dataset.
        """
        movies = []

        while(len(movies) < amount):
            movie = self.get_movie_stats(
                random.choice([x for x in self.titles.keys()][:69])
            )

            # evict films without a poster
            if movie['Meta']['Plot'] not in ['Unknown', 'N/A'] \
                and movie not in movies:
                movies.append(movie)

        return movies

    def get_ranking(self, movieId):
        """
            Returns the ranking of a movie based on its rating.
        """
        if movieId not in self.get_top_rated():
            return '??'

        return self.get_top_rated().index(movieId)

    def _cache_boxplot(self):
        """
            Create a cache for all boxplot values.
        """
        ratings = [self.get_ratings(x) for x in self.get_titles()]
        rating_data = {}

        for rating in ratings:
            yearData = rating.keys()
            for elem in yearData:
                #print(yearData)
                rating_data.update({elem: rating_data.get(elem, []) + [rating[elem][1]]})

        rating_data.update({'Time': self._current_time()})

        f = open(_CACHE_DIR + 'boxplot.json', "w+")
        f.write(json.dumps(rating_data, indent=4, sort_keys=True))
        f.close()

        return rating_data

    def _boxplot_from_cache(self):
        """
            Load boxplot values from cache.
        """
        with open(_CACHE_DIR + 'boxplot.json') as f:
            return json.load(f)

    def compute_boxplot(self):
        """
            Compute all boxplot data (ratings per year).
        """
        if not os.path.isfile(_CACHE_DIR + 'boxplot.json'):
            data = self._cache_boxplot()

        if 'data' not in locals():
            data = self._boxplot_from_cache()

            # If the cache is older then 1 week, re-cache.
            if (self._current_time() - data['Time'] >= 604800000):
                data = self._cache_boxplot()

        return data

#! /usr/bin/python
import services

class Stats:

    def computeRatings(averages, perYear=True):
        """
            Computes the average rating based on a list of ratings. If the perYear
            parameter is set to true, the average rating per year will be calculated.
        """
        if perYear:
            result = {}

            for item in averages:
                result[item] = averages[item][0] / averages[item][1]

            return result

        total = ratings = 0
        for item in averages:
            total += averages[item][0]
            ratings += averages[item][1]

        return total / ratings

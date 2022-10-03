def convert_minute_to_seconds(timeString):
        splittedTime = timeString.split(':')
        return int( splittedTime[0] ) * 60 + int( splittedTime[1] )
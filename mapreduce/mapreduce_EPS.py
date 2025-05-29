from mrjob.job import MRJob
from mrjob.step import MRStep

class MREPSQuality(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper, reducer=self.reducer)
        ]

    def mapper(self, _, line):
        fields = line.strip().split(',')
        try:
            if fields[0] == "codigo":
                return
            EPS = fields[2]
            WaitingTime = int(fields[7])
            yield EPS, (WaitingTime, 1)
        except:
            pass



    def reducer(self, EPS, values):
        total_wait_Time = 0
        max_wait_time = 0
        count = 0
        for wTime, c in values:
            total_wait_Time += wTime
            count += c
            if wTime > max_wait_time:
                max_wait_time = wTime
        yield EPS, {
            "avg_wait_time": round(total_wait_Time/ count, 2),
            "max_wait_time": max_wait_time
        }


if __name__ == '__main__':
    MREPSQuality.run()

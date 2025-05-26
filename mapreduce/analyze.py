from mrjob.job import MRJob
from mrjob.step import MRStep

class MRClimateAnalysis(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper,
                   reducer=self.reducer)
        ]

    def mapper(self, _, line):
        fields = line.strip().split(',')
        try:
            if fields[0] == "time" or fields[0].startswith("latitude") or len(fields) < 2:
                return
            fecha_completa = fields[0].strip()
            temp = float(fields[1].strip())
            fecha = fecha_completa.split(' ')[0]  
            yield fecha, (temp, 1)
        except:
            pass



    def reducer(self, fecha, values):
        total_temp = 0
        count = 0
        for temp, c in values:
            total_temp += temp
            count += c
        yield fecha, {
            "avg_temp": round(total_temp / count, 2)
        }


if __name__ == '__main__':
    MRClimateAnalysis.run()

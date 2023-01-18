from gui.model.ProgressLogger.TimeLogger import TimeLogger


class RunProgLogger(TimeLogger):
    def write(self, log_entry):
        try:
            prog_perc = log_entry.split('%')[0].strip()
            prog_nums = log_entry.split('/')
            to_do = prog_nums[0].split(' ')[-1]
            done = prog_nums[1].split(' ')[0]
            self.add_to_stack('Traces analyzed: {}/{}, ({}%)'.format(to_do, done, prog_perc))
            # remaining = log_entry.split('<')[-1].split(',')[0].split(':')[::1]
            # elapsed = log_entry.split('<')[0].split('[')[1].split(':')[::1]
            # self.add_to_stack('elapsed: {}m {}s, remaining: {}m {}s'.format(int(elapsed[0]), int(elapsed[1]),
            #                                                                 int(remaining[0]), int(remaining[1])))
        except Exception as e:
            pass

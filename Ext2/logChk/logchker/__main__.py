from dynatrace_extension import Extension, Status, StatusValue
from datetime import timedelta, datetime
import re, sys, os, time


osss = sys.platform
if osss == "linux":

    def mt_cnt(filename, pattern):
        return int(os.popen(f"grep {pattern} {filename} |wc -l").read())

else:
    print(osss)

    def mt_cnt(filename, pattern):
        with open(filename, "r") as file:
            fileread = file.read()
            matches = re.findall(pattern, fileread)
            return len(matches)


class ExtensionImpl(Extension):

    def fastcheck(self) -> Status:
        """
        This is called when the extension runs for the first time.
        If this AG cannot run this extension, raise an Exception or return StatusValue.ERROR!
        """
        return Status(StatusValue.OK)

    def initialize(self):
        self.report_metric(
            "my_metric_test", 1, dimensions={"my_dimension": "dimension1"}
        )
        self.logger.info("Initialized Extension; checking for endpoints")
        for endpoint in self.activation_config["endpoints"]:
            self.logger.info("Ifl checking for endpoints")
            check_interval = float(endpoint["check_interval"])
            log_files = endpoint["log_files"]
            log_patterns = endpoint["log_patterns"]
            dept_name = endpoint["dept_name"]
            metric_name = "custom.log.pattern." + dept_name
            self.schedule(
                self.check_log,
                timedelta(minutes=check_interval),
                (log_files, log_patterns, metric_name),
            )
            self.logger.info(
                f"interval collection method started for logchker.{log_files,log_patterns,metric_name,check_interval}"
            )

    def check_log(self, log_files, log_patterns, metric_name):
        count_list = []
        self.logger.info(
            f"check_log method started for logchker with log_files: '{log_files}'."
        )

        #        for endpoint in self.activation_config["endpoints"]:
        #        self.logger.info(f"Running endpoint with log_files: '{log_files}'")

        def search_patterns_in_log(log_file):
            if os.path.exists(log_file):
                read_permission = os.access(log_file, os.R_OK)
                self.logger.info(f"Permission for {log_file} : {read_permission}")
                for pattern in log_patterns:
                    starttime = time.perf_counter()
                    count = mt_cnt(log_file, pattern)
                    endtime = time.perf_counter()
                    if count > 0:
                        count_list.append((log_file, pattern, count))
                        self.logger.info(
                            f"File {log_file} == Time : {endtime-starttime} "
                        )
                        # print(metric_name, count, dimensions={"pattern":pattern,"logfile":log_file})
            else:
                print(f"Log file {log_file} not found", file=sys.stderr)

        for log_file in log_files:
            search_patterns_in_log(log_file)
            for log_file, pattern, count in count_list:
                self.report_metric(
                    metric_name,
                    count,
                    dimensions={"pattern": pattern, "logfile": log_file},
                )
            count_list.clear()

        # self.report_metric("my_metric", 1, dimensions={"my_dimension": "dimension1"})
        self.logger.info(f"check_log method ended for logchker for {log_files}.")


def main():
    ExtensionImpl(name="logchker").run()


if __name__ == "__main__":
    main()

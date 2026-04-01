- check @statistic in the corresponding NED file to see what statistics are collected.
The neames of the statistics are composed from the propery index + the recording mode.
e.g. @statistic[endToEndDelay](..., record=mean,last) -> endToEndDelay:mean , endToEndDelay:last
- you can add more recording modes using configuration option using `**.result-recording-modes=+vector`.
- you can use python to load result files into pandas dataframes: import omnetpp.scave.results
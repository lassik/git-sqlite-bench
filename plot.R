png('millisec-hist.png')
hist(scan('work/millisec'))
dev.off()

png('millisec-trend.png')
plot(scan('work/millisec'), log='y')
dev.off()

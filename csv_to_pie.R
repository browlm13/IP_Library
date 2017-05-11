# Simple Pie Chart
# Pie Chart from csv format of line : label,value #end with newline
elements <- read.csv("test_piecsv.csv", header=F)
pie(t(elements[2]), labels = t(elements[1]), main="Title")

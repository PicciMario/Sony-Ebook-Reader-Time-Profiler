set xdata time
set timefmt "%Y-%m-%d-%H:%M:%S"
set format x "%d/%m\n%H:%M:%S"

set xrange["2011-09-20-00:00":"2011-09-28-00:00"]
set yrange[0:30]

set term pdf size 7,2
set output "output.pdf"

set pointsize 0.8
set grid

set title "Ebook reader usage" font "Times-Roman,10"

plot 	"out.dat" 	using 1:2 with impulses notitle, \
		"out.dat" 	using 1:2 with points pointtype 7 notitle#, \
#		"" 			using 1:($2+0.8):2 with labels notitle
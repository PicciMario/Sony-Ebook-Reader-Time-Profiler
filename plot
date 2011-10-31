set xdata time
set timefmt "%Y-%m-%d-%H:%M:%S"
set format x "%d/%m\n%H:%M:%S"

#set xrange["2011-09-29-13:18":"2011-09-29-13:30"]
set yrange[0:50]

set term pdf
set output "output.pdf"
set pointsize 1

set title "Ebook reader usage"

plot 	"out.dat" 	using 1:2 with impulses notitle, \
		"out.dat" 	using 1:2 with points pointtype 7 notitle#, \
#		"" 			using 1:($2+0.8):2 with labels notitle
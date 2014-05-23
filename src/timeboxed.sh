#!/bin/bash

months=(5)
for month in ${months[@]}; do
    monthplus1=$month+1
    this_month=`printf "%02d" $month`
    next_month=`printf "%02d" $(expr $month + 1)`

    from_date=`date -j -f "%Y-%m-%d" "2014-$this_month-01" +"%s"`
    to_date=`date -j -f "%Y-%m-%d" "2014-$next_month-01" +"%s"`

    timespan=$from_date,$to_date

    n_clusters=(3 4 5 6 7 8 9 10)
    echo ./main.py --reset --build -t $timespan
    ./main.py --reset --build -t $timespan
    for n in ${n_clusters[@]}; do
        cmd="./main.py -t $timespan --algorithm k_means --n-clusters $n --normalize"
        echo "Executing for month $month: $cmd"
        $cmd
    done
done

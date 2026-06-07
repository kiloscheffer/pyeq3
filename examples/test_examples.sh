#!/bin/bash

fulldir=`pwd`

# use numdiff but fall back to diff if not found:
which numdiff >/dev/null
if [ $? -eq 0 ]
then
  diffcmd="numdiff -r 2e-5 -s ' \t\n[],'"
else
  diffcmd="diff"
  echo "WARNING: numdiff not found, please install! Falling back to diff."
fi

if [ -z $PYTHON ]
then
  PYTHON=python
fi

function testit {
t=$1

if [ "$t" == "__init__.py" ]
then
return 0
fi

fulldir=$2
#echo "*** testing $t ..."
($PYTHON <<EOF
import matplotlib as m
import numpy as np
m.use('Template')
VERBOSE=1
RUNNING_TESTS=1
with open('$t') as f:
    CODE = compile(f.read(), '$t', 'exec')
    exec(CODE)
EOF
) >$t.tmp 2>$t.tmp.error
ret=$?
grep -v "^$" $t.tmp.error >>$t.tmp #append non-empty error messages to output
rm -f $t.tmp.error

grep -v "which is a non-GUI backend" $t.tmp | grep -v "plt.show()" > tmpfile
mv tmpfile $t.tmp

if [ "$ret" -ne 0 ]
then
  echo "!  $t ... FAIL";
  cat $t.tmp;
  return 1;
else

  sedthing="s#$fulldir#pyeq3#g"
  sed -i.bak -e $sedthing $t.tmp #remove the absolute path from warnings
  sed -i.bak -e "s/.py:[0-9]*:/.py:/g" $t.tmp #remove line numbers
  sed -i.bak -e 's/<stdin>:[0-9]*: //g' $t.tmp #remove line numbers
  sed -i.bak -e '/OptimizeWarning: Covariance of the parameters could not be estimated/d' $t.tmp # remove covariance warning
  sed -i.bak -e '/scipy.optimize.curve_fit/d' $t.tmp # remove rest of covariance warning
  sed -i.bak -e '/UserWarning: FigureCanvasTemplate/d' $t.tmp #remove plotting nonsense

  rm -f $t.tmp.bak

  (eval $diffcmd $t.tmp $fulldir/ref/$t.out >/dev/null && rm $t.tmp && echo "  $t ... output ok"
  ) || {
  echo "!  $t ... FAIL";
  echo "Check: `pwd`/$t.tmp $fulldir/ref/$t.out";
  eval $diffcmd $t.tmp $fulldir/ref/$t.out | head
  return 2;
  }

fi
}


# create a list of specific tests to run and not test against output:
run_only_list="Simple/FitOneNamedEquation_2D.py
               Simple/FitOneNamedEquation_3D.py
               Simple/FitUserCustomizablePolynomial_2D.py
               Simple/FitUserData_2D.py
               Simple/FitUserDefinedFunction_2D.py
               Simple/FitWeightedData_2D.py
               Simple/OutputAllSourceCode.py
               Simple/Spline_3D.py"

$PYTHON --version
for test in `ls */*.py`
do
    # skip tests in certain directories that are long or not expected to pass:
    [ `echo $test | grep -c "^AnimatedGIF/"` -ne 0 ] && echo "  *** skipping $test !" && continue
    [ `echo $test | grep -c "^Cluster/"` -ne 0 ] && echo "  *** skipping $test !" && continue
    [ `echo $test | grep -c "^Complex/"` -ne 0 ] && echo "  *** skipping $test !" && continue
    [ `echo $test | grep -c "^IPython/"` -ne 0 ] && echo "  *** skipping $test !" && continue
    [ `echo $test | grep -c "^List/"` -ne 0 ] && echo "  *** skipping $test !" && continue
    [ `echo $test | grep -c "^NodeJS/"` -ne 0 ] && echo "  *** skipping $test !" && continue
    [ `echo $test | grep -c "^Parallel/"` -ne 0 ] && echo "  *** skipping $test !" && continue

    # skip certain tests that are long or not expected to pass:
    [ $test == "GenerateOutput/generateOutput.py" ] && echo "  *** skipping $test !" && continue
    [ $test == "FitMultipleFunctions/fit_all_functions.py" ] && echo "  *** skipping $test !" && continue

    # if test is in the run_only_list, then run it and send output to /dev/null
    [ `echo $run_only_list | grep -c "$test"` -ne 0 ] && echo "  $test ... run successful" && python $test >/dev/null 2>&1 && continue
    testit $test $fulldir || exit 1
done

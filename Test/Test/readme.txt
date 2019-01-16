start_jobs is a short perl script to test running a parameter sweep on Fiji. 

to run the code:

1) make sure you can login to Fiji via ssh (e.g., ssh identKey@fiji.colorado.edu)
2) copy the test files (scp test.m start_jobs identKey@fiji.colorado.edu:./Test/)
3) once your files are in your Fiji home directory, type ‘start_jobs’ to run the test
4) type ‘Test_a0.*/test.txt’ to see the output

correct output:

0.34,1.34,2.34
0.34,1.34,2.68
0.34,1.68,2.34
0.34,1.68,2.68
0.68,1.34,2.34
0.68,1.34,2.68
0.68,1.68,2.34
0.68,1.68,2.68
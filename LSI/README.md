#Project 1: Latent Semantic Indexing
##Requirements
Linux/gcc/matlab

##Instructions
1. Build the Indri project by moving to the indri-5.6/ directory and typing "make" or "gmake". Warning: there will be a lot of warnings. Warning: live without warning.
1. Next set the index location inside the <index> brackets near the top of the parameter.xml to a location on your computer with plenty of space. (e.g. <index>my/index/directory/</index>).
1. In the indri-5.6/buildindex/ directory type "IndriBuildIndex ../../parameter.xml" to build the indri inverted list index.
1. In the indri-5.6/app/ directory type "make" to compile my code.
1. In the same directory type "TFIDFMatrix /my/index/directory/" but make sure you specify the actual directory where your index resides. This will generate a TFIDFMatrix.dat which is a sparse matrix representation the TFIDF matrix.
1. In the same directory open matlab and type "GenerateLSI". The prompt will ask you to enter a k-value. This k-value will be used to specify the number of concepts in the LSI index. It must be less than the number of documents in your corpus. The number of documents in our corpus is 2500 but running the singular value decomposition on this many items will take many hours so you will want to pick a value around 300-400. This generates the LSIMatrix.dat which are the U and S matrices multiplied and the VMatrix.dat which is just the vMatrix (For more information about LSI go [here](http://www1.se.cuhk.edu.hk/~seem5680/lecture/LSI-Eg.pdf). This segment does the SVD computation and it would be nice to have this be done without requireing matlab and will be a future development.
1. In the same directory type "convertFullToSparse -mf LSIMatrix.dat" and then do the same for the VMatrix.dat. This will convert these matrices into sparse matrices.

You now have all the data, matrices, to successfully evaluate queries.

##Query Evaluation

###Using a Query File.
To simplify queries I have defined a query file that can be read in and automatically evaluate multiple queries at once and output all the results into an out directory. The query files use # as a comment but it must be in the first position of the line. For each query in the query file make to add a query id, one space, then your query. (e.g. 45 computer science activities). See queries.txt under indri-5.6/app.

###TFIDF Evaluation
1. In the indri-5.6/app directory type "QueryEvaluation -mf TFIDFMatrix.dat -r /my/index/directory -qf queries.txt"
1. If you would like to specify one query at a time you may typethe following in the same directory "QueryEvaluation -mf TFIDFMatrix.dat -r /my/index/directory -q 66 This is my query" where 66 will uniquely identify this query and output it to the output\_tfidf\_66.html file. 

###LSI Evaluation
1. In the indri-5.6/app directory type "QueryEvaluation -mf LSIMatrix.dat -vf VMatrix.dat -r /my/index/directory -qf queries.txt"
1. If you would like to specify one query at a time you may typethe following in the same directory "QueryEvaluation -mf LSIMatrix.dat -vf VMatrix.dat -r /my/index/directory -q 66 This is my query" where 66 will uniquely identify this query and output it to the output\_lsi\_66.html file. 

Doing the above commands will generate values in the out file related to your query based on the query id and the method being used. For example the values output\_tfidf\_61.html will be webpage that has the rankings of the pages that relate to query 61.

#include "indri/Repository.hpp"
#include "indri/CompressedCollection.hpp"
#include "indri/LocalQueryServer.hpp"
#include "indri/ScopedLock.hpp"
#include "indri/QueryEnvironment.hpp"
#include "indri/DiskIndex.hpp"
#include <iostream>
#include <fstream>
#include <math.h>

int main(int argc, char *argv[]){
  if(argc < 2){ return -1;}

  indri::collection::Repository r; 
  std::string repName = argv[1];

  r.openRead( argv[1] );

  indri::collection::Repository::index_state state = r.indexes();
  indri::index::Index* index = (*state)[0];
  indri::index::DocListFileIterator* iter = index->docListFileIterator();

  ofstream MyFile;
  int N = index->documentCount();
  int df, tf;

  iter->startIteration();
  MyFile.open("TFIDFMatrix.dat", ios::out);
  while( !iter->finished() ) {
    indri::index::DocListFileIterator::DocListData* entry = iter->currentEntry();
    df = entry->termData->corpus.documentCount;
    entry->iterator->startIteration();
    while( !entry->iterator->finished() ){
	indri::index::DocListIterator::DocumentData* doc = entry->iterator->currentEntry();
	tf = doc->positions.size();
	lemur::api::TERMID_T tid = index->term(entry->termData->term);
	if(tid <= 0 || tid >index->uniqueTermCount()){
	  cout << "ERMAGERD!!" << endl;
	}
	double tfidf = tf * log2((double)N/df);
	MyFile << tid << "\t" << doc->document << "\t" << tfidf  << endl;
	entry->iterator->nextEntry();
    }
    iter->nextEntry();
  }
  
  MyFile << index->uniqueTermCount() << "\t" << N << "\t0.0"; 

  delete iter;
  MyFile.close();
  r.close();
}

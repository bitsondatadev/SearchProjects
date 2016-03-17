#include "indri/Repository.hpp"
#include "indri/CompressedCollection.hpp"
#include "indri/LocalQueryServer.hpp"
#include "indri/ScopedLock.hpp"
#include "indri/QueryEnvironment.hpp"
#include "indri/DiskIndex.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <math.h>
#include <string>
#include <queue>
#include <sys/stat.h>
#include <sys/types.h>

/**
 * docrank class to save the top ranking docs in priority queue and ranke by similarity
 */
class docrank {
public:
 lemur::api::DOCID_T did;
 std::string path;
 double sim;
 docrank(lemur::api::DOCID_T did, std::string path, double sim){
	this->did = did;
	this->path = path;
	this->sim = sim;
 }
 double getSim() const{
	return sim;
 }
};

void processQuery(std::string);
bool operator <(const docrank&, const docrank&);

indri::collection::Repository r; 
struct stat info;
bool isLSI;
int k = 0;
indri::utility::HashTable< lemur::api::TERMID_T, indri::utility::HashTable< lemur::api::DOCID_T, double>* > matMap;
indri::utility::HashTable< lemur::api::TERMID_T, indri::utility::HashTable< lemur::api::DOCID_T, double>* > vMap;

int main(int argc, char *argv[]){
  std::string repName = "";
  std::string queryFileName = "";
  std::string query = "";
  std::string matrixFileName = "";
  std::string vMatrixFileName = "";

  //Argument processing
  for(int i = 1; i < argc; i++){
    if(!strcmp(argv[i], "-r")){
	repName = argv[++i];
    }else if(!strcmp(argv[i], "-qf")){
	queryFileName = argv[++i];
    }else if(!strcmp(argv[i], "-q")){
	query = argv[++i];
    }else if(!strcmp(argv[i], "-mf")){
	matrixFileName = argv[++i];
    }else if(!strcmp(argv[i], "-vf")){
	vMatrixFileName = argv[++i];
    }
  }
  
  if(repName.empty() || matrixFileName.empty() || queryFileName.empty() && query.empty()){
    cout << "Usage: QueryEvaluation " 
         << "-mf <TFIDF_Matrix_File | LSI_Matrix_File> "
         << "-vf <V_Matrix_File> "
         << "-r <Index_File> "
         << "(-qf <Query_File> | -q <Query>)" << endl;
    return -1;
  }

  r.openRead( repName );

  std::string line; 
  ifstream matFile;
  lemur::api::TERMID_T tid;
  lemur::api::DOCID_T did;
  double val;


/**
 * Import either TFIDF Matrix or LSI Matrix if doing LSI
 */ 
  matFile.open(matrixFileName.c_str());
  while(!matFile.eof()){
    std::getline(matFile, line);
    istringstream iss(line);
    iss >> tid;
    iss >> did;
    iss >> val;
    if(val != 0){
      indri::utility::HashTable<lemur::api::DOCID_T,double>** testPtr = matMap.find(tid);
      if(testPtr == 0){
	testPtr = matMap.insert(tid, new indri::utility::HashTable<lemur::api::DOCID_T,double>());
      }
      indri::utility::HashTable<lemur::api::DOCID_T,double>* docMapPtr = *testPtr;
      docMapPtr->insert(did, val);
    }
  }
  matFile.close();
  
/**
 * Import vMatrix if doing LSI
 */ 
  if(!vMatrixFileName.empty()){//specified vMatrix, assume LSI 
    isLSI = true;
    matFile.open(vMatrixFileName.c_str());
    while(!matFile.eof()){
      std::getline(matFile, line);
      istringstream iss(line);
      iss >> tid;
      iss >> did;
      iss >> val;
      if(val != 0){
        indri::utility::HashTable<lemur::api::DOCID_T,double>** testPtr = vMap.find(tid);
        if(testPtr == 0){
          testPtr = vMap.insert(tid, new indri::utility::HashTable<lemur::api::DOCID_T,double>());
        }
        indri::utility::HashTable<lemur::api::DOCID_T,double>* docMapPtr = *testPtr;
        docMapPtr->insert(did, val);
      }
      if(tid==1){
	k++;
      }
    }
    matFile.close();
  }//else we didn't specify vMatrix assume TFIDF

/**
 * Import queries from file or query from command line
 */ 

 if(!queryFileName.empty()){
     //query file
     ifstream queryFile;
     queryFile.open(queryFileName.c_str());
     while(!queryFile.eof()){
       std::getline(queryFile, line); 
       if(!line.empty() && line[0] != '#' && line[0] != ' '){
 	processQuery(line);      
       }
     }
     queryFile.close();
  }
  
  if(!query.empty()){
     //manual query
     processQuery(query);      
  }

  /**
   * free hashmaps on the heap
   */ 
  indri::utility::HashTable<lemur::api::TERMID_T, indri::utility::HashTable<lemur::api::DOCID_T, double>* >::iterator i = matMap.begin();
  for(; i != matMap.end(); i++){
	delete *i->second;
  }

  i = vMap.begin();
  for(; i != vMap.end(); i++){
	delete *i->second;
  }
  
  return 0;
}//end main()

void processQuery(std::string query){
  indri::utility::HashTable< lemur::api::TERMID_T, indri::utility::HashTable< lemur::api::DOCID_T, double>* >* matMapPtr;
  indri::utility::HashTable< int, double>* queryMapPtr;
  indri::utility::HashTable< int, double> queryMap;
  indri::utility::HashTable< int, double> queryResultMap;
  std::priority_queue<docrank> docQ;
  istringstream iss(query);
  int queryNumber;
  std::string term;

  indri::index::Index* index = (*r.indexes())[0];
  iss >> queryNumber;
  
  /**
   * create condensed query "vector" using HashTable by excluding terms that do not occur
   */ 
  while(iss >> term){
    std::string stemTerm = r.processTerm(term);
    lemur::api::TERMID_T tid = index->term(stemTerm);
    double* termVal = queryMap.find(tid);
    if(termVal == 0){
      termVal = queryMap.insert(tid,0.0);
    }
    (*termVal)++;
  }

  /**
   * Prep matrices and vectors for cosine similarity step
   */
  if(isLSI){
	  //multiply q^T by U_k * inv(S_k) to get the 
	  for(indri::utility::HashTable< int, double>::iterator i = queryMap.begin(); i != queryMap.end(); i++){
		int tid = *i->first;
		int termCount = *i->second;
		//cout << "termid: " <<tid << " term: " << index->term(tid) << " count: " << termCount << endl;	
		if(tid != 0){
		    indri::utility::HashTable< lemur::api::DOCID_T, double>** testPtr = matMap.find(tid);
		    if(testPtr==0){
			cout << "ERMAGERD?!?!" << tid << endl;
		    }else{
			indri::utility::HashTable< lemur::api::DOCID_T, double>* docMapPtr = *testPtr;
			for(indri::utility::HashTable< lemur::api::DOCID_T, double>::iterator j = docMapPtr->begin(); j != docMapPtr->end(); j++){
			  lemur::api::DOCID_T conceptid = *j->first;
			  double val = *j->second;
			  double* result = queryResultMap.find(conceptid);
			  if(result == 0){
				result = queryResultMap.insert(conceptid, 0);
			  }
			  *result += termCount * val;
			}
		    }
		}
	  }
  	  //set vMap to *matMapPtr so calculation below can be generic
	  matMapPtr = &vMap;
	  queryMapPtr = &queryResultMap;
  }else{
  	//set matMap to *matMapPtr so calculation below can be generic
	matMapPtr = &matMap;
	queryMapPtr = &queryMap;
  }

  /**
   * Cosine Similarity
   *
   */ 

  double* sumNum = new double[index->documentCount() + 1]();
  double* sumDen = new double[index->documentCount() + 1]();
  indri::utility::HashTable<lemur::api::TERMID_T, indri::utility::HashTable<lemur::api::DOCID_T, double>* >::iterator i = matMapPtr->begin();
  for(; i != matMapPtr->end(); i++){
  	//conceptid is actually termid for TFIDF
	int conceptid = *i->first;
	indri::utility::HashTable< lemur::api::DOCID_T, double>** testPtr = i->second;
	if(testPtr != 0){
		indri::utility::HashTable< lemur::api::DOCID_T, double>* docMapPtr = *testPtr;
		double* val = queryMapPtr->find(conceptid);
		if(val != 0 && *val != 0.0){
			//calculate numerator and add to numsum and calculate numdem with query
			for(indri::utility::HashTable< lemur::api::DOCID_T, double>::iterator j = docMapPtr->begin(); j != docMapPtr->end(); j++){
				lemur::api::DOCID_T did = *j->first;
				sumNum[did] += (*val * *j->second); 
				sumDen[did] += sqrt(*val * *val + *j->second * *j->second);
			}
		}else{
			//calculate denominator without query
			for(indri::utility::HashTable< lemur::api::DOCID_T, double>::iterator j = docMapPtr->begin(); j != docMapPtr->end(); j++){
				lemur::api::DOCID_T did = *j->first;
				sumDen[did] += sqrt(*j->second * *j->second);
			}
		}
	}
  }

  for(int i = 1; i <= index->documentCount(); i++){
  	indri::collection::CompressedCollection* collection = r.collection();
	indri::api::ParsedDocument* doc = collection->retrieve( i );
	for(size_t j = 0; j < doc->metadata.size(); j++){
		if(!strcmp(doc->metadata[j].key,"path")){
			docQ.push(docrank(i,(const char*)doc->metadata[j].value ,sumNum[i]/sumDen[i]));
			j = doc->metadata.size();
		}
	}
  }

  delete sumNum;
  delete sumDen;
  
  /**
   * Output the top 20 query results
   */
  
  std::string outputFolder = "./out";
  if( stat( outputFolder.c_str(), &info ) == 0){
    std::ostringstream oss;
    if(isLSI){
    	oss << outputFolder << "/output_lsi_" << queryNumber << ".html";
    }else{
    	oss << outputFolder << "/output_tfidf_" << queryNumber << ".html";
    }
    std::ofstream queryout(oss.str().c_str());
    queryout << "<html><body>" << endl << "<h1>Broogle - Brian's Google</h1>" << endl;
    queryout << "<h2>Query " << queryNumber << ": </h2> <p>" << query << "</p>" << endl;
    oss.str(std::string());
    for(int i = 0; i < 20; i++){
	  docrank doc = docQ.top();
	  docQ.pop();

	  oss << doc.did << ".html";
    	  queryout << "Rank: " << i + 1 
	  << "<a href =\"" << oss.str() << "\" target=\"_blank\"> " << doc.path << " </a> "
	  << " Score: " << doc.sim << 
	  " Indri DocId: " << doc.did << "</br></br>" << endl; 
	  
    	  oss.str(std::string());
	  oss << outputFolder << "/" << doc.did << ".html";
          std::ifstream fin( doc.path.c_str() ) ;
          std::ofstream fout( oss.str().c_str() ) ;
          std::string line ;
	  while( std::getline( fin, line ) ){
	    fout << line << '\n' ;
	  }
    	  oss.str(std::string());
    }
    queryout << "</body></html>";
  }else{
    cout << "./out/ directory not created. Printing results to console..." << endl;

    cout << "Query " << " \"" << query << "\"" << endl;
    for(int i = 0; i < 20; i++){
	  docrank doc = docQ.top();
	  docQ.pop();
	  cout << "Rank: " << i + 1 << " " << "DocID: " << doc.did << " Score: " << doc.sim << " Path: " << doc.path << endl;
    }
  }
}//end processQuery

bool operator <(const docrank& lhs, const docrank& rhs){
	return lhs.sim < rhs.sim;
 }

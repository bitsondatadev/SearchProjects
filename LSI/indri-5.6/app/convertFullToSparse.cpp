#include <iostream>
#include <fstream>
#include <sstream>
#include <math.h>
#include <string>
#include <string.h>
#include <queue>


int main(int argc, char *argv[]){
  std::string matrixFileName = "";
  //Argument processing
  for(int i = 1; i < argc; i++){
    if(!strcmp(argv[i], "-mf")){
	matrixFileName = argv[++i];
    }
  }
  
  if(matrixFileName.empty()){
    std::cout << "Usage: -mf <TFIDF_Matrix_File> " << std::endl;
    return -1;
  }
  std::ostringstream oss;

  std::string line; 
  std::ifstream matFile;
  matFile.open(matrixFileName.c_str());
  double val;
  int tid = 1;
  while(!matFile.eof()){
    std::getline(matFile, line);
    std::istringstream iss(line);
    int did = 1;
    while(iss >> val){
	if(val != 0.0){
		oss << tid << "\t" << did << "\t" << val << std::endl;
	}
	did++;
    }
    tid++;
  }
  matFile.close();
  std::ofstream oMatFile;
  if(remove(matrixFileName.c_str()) == 0){
 	oMatFile.open(matrixFileName.c_str());
	std::string s = oss.str();
  	oMatFile << s;
  	oMatFile.close();
	std::cout << "Successfully converted to sparse matrix!!" << std::endl;
  }else{
	std::cout << "No luck..." << std::endl;
  }

  return 0;
}

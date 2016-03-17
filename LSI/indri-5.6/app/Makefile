include ../MakeDefns
SHARED=
INCPATH=-I../include $(patsubst %, -I../contrib/%/include, $(DEPENDENCIES))
LIBPATH=-L../obj  $(patsubst %, -L../contrib/%/obj, $(DEPENDENCIES))
LIBS=-lindri $(patsubst %, -l%, $(DEPENDENCIES))
APP1=TFIDFMatrix
APP2=QueryEvaluation
APP3=convertFullToSparse

all:
	$(CXX) $(CXXFLAGS) $(APP1).cpp -o $(APP1) $(LIBPATH) $(LIBS) $(CPPLDFLAGS)
	$(CXX) $(CXXFLAGS) $(APP2).cpp -o $(APP2) $(LIBPATH) $(LIBS) $(CPPLDFLAGS)
	$(CXX) $(CXXFLAGS) $(APP3).cpp -o $(APP3) $(LIBPATH) $(LIBS) $(CPPLDFLAGS)

install:
	$(INSTALL_PROGRAM) $(APP1) $(bindir)
	$(INSTALL_PROGRAM) $(APP2) $(bindir)
	$(CXX) $(CXXFLAGS) $(APP3).cpp -o $(APP1) $(LIBPATH) $(LIBS) $(CPPLDFLAGS)

clean:
	rm *.dat 
	rm -f $(APP1)
	rm -f $(APP2)
	rm -f $(APP3)

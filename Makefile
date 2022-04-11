create: 
	singularity build --fakeroot searchOytser.sif searchOytser.def
run:
	./searchOytser.sif

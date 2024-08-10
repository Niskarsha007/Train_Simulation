(define
	(problem trainpddl)
	(:domain trainpddl)
	(:objects
		branch1 - branch
		station1 station3 station6 station8 station10 station13 - station
		tn - train
	)
	(:init (isAt tn branch1) (isBranch station1 branch1) (isBranch station3 branch1) (isBranch station6 branch1) (isBranch station8 branch1) (isBranch station10 branch1) (isBranch station13 branch1))
	(:goal (and (visited tn station8) (visited tn station1)))
)

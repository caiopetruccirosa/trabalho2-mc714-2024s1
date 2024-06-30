package consensus

type NodeState int

const (
	FOLLOWER_STATE NodeState = iota
	CANDIDATE_STATE
	LEADER_STATE
)

func RequestVote() {

}

func SendVote() {

}

func AppendEntries() {

}

func SendAppendEntries() {

}

func SendHeartbeat() {

}

func StartElection() {

}

func StartLeader() {

}

func StartFollower() {

}

func StartCandidate() {

}

func StartConsensus() {

}

func StartRaft() {

}

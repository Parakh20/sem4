# EE465 Quiz Cheatsheet

Based only on:
- `Consensus.pdf`
- `EthereumBlocks.pdf`
- `EVM.pdf`
- `SolidityTutorial.pdf`
- `TornadoCash.pdf`

This sheet is organized as a dense revision note, not as a short summary. It tries to preserve all directly stated definitions, formulas, workflows, and code-level facts from the specified PDFs.

## 1. Consensus Protocols

### 1.1 Core idea
- Consensus protocols let multiple computers connected by a network stay in sync.
- The computers are called nodes.
- The network may be unreliable:
  - packet drops
  - delays
- Some nodes may be malicious and may deviate from the protocol.
- Assumptions stated in the deck:
  - semi-reliable point-to-point communication between nodes
  - secure digital signatures are available

### 1.2 State Machine Replication (SMR)
- SMR was first studied in the 1980s.
- Clients submit transactions to one or more nodes.
- Each node maintains a local append-only data structure representing an ordered sequence of transactions. This is the node's history.
- Goal: all nodes must have identical local histories.
- If all nodes start from the same initial state, then applying the same transactions in the same order gives the same final state.
- SMR protocol requirements:
  - consistency: all nodes agree on the same history
  - liveness: every valid transaction submitted by a client is eventually added to the history

### 1.3 Synchronous setting with honest nodes
- Assumption 1: permissioned network
  - the set of nodes running the protocol is fixed and known
  - denote nodes by `{1, 2, ..., n}`
- Why study permissioned networks even though blockchains are permissionless?
  - impossibility results in the easier permissioned setting also apply to the harder permissionless setting
  - permissionless consensus protocols use ideas from the permissioned setting
- Assumption 2: public key infrastructure
  - each node has a public key known to all other nodes
- Assumption 3: synchronous network
  - shared global clock
  - if time is broken into time steps, all nodes agree on the current time step
  - bounded delays: a message sent at time step `t` arrives before time step `t + 1`
  - message reordering is still possible
- Assumption 4: all nodes are honest
  - all nodes run the protocol without deviations or errors

### 1.4 Two faulty SMR protocols

#### Faulty protocol A: no inter-node communication
- Nodes do not communicate with each other.
- As soon as a node receives a client request, it appends the transaction to its own history.
- This works only in the special case where all clients submit to all nodes at the same time.
- Consistency fails if:
  - a client submits requests only to a strict subset of the nodes, or
  - requests arrive in different orders at different nodes

#### Faulty protocol B: one permanent leader
- One node, say node 1, is fixed as leader.
- At the beginning of each time step, the leader sends an ordered list of known transactions to all nodes.
- Every node appends that list to its history.
- This achieves consistency because all histories are identical.
- This does not achieve liveness if the client submits a request to a non-leader node.

### 1.5 SMR via rotating leaders
- In each time step, choose the leader in round-robin fashion.
- In time step `t`, leader ID is `1 + (t mod n)`.
- At the beginning of each time step, the leader sends an ordered list of new transactions it knows about.
- "New" means not yet added to the history.
- Empty list is allowed.
- Before the next time step begins, every node, including the leader, appends this list to its history.
- Consistency holds because all nodes append the same list in each step.
- Liveness holds because:
  - if a client submits to node `i`
  - then node `i` eventually becomes leader
  - if the transaction has not yet been included, node `i` will broadcast it then

### 1.6 Fault types and Byzantine nodes
- The assumption that all nodes are honest is unrealistic.
- Fault types:
  - crash fault: node stops working at some time `t`
  - omission fault: node does not send some messages it should send
  - Byzantine fault: node can deviate arbitrarily
- Even Byzantine nodes cannot forge digital signatures.
- Historical note:
  - Istanbul was previously called Byzantium
  - Lamport, Shostak, and Pease introduced the Byzantine generals story in 1982
- Relaxed assumption:
  - the number of Byzantine nodes is at most `f`
  - `f = 0` corresponds to all nodes being honest
  - `f` is assumed known
  - the identities of the Byzantine nodes are not known
  - the set of Byzantine nodes is fixed
- Important point from the slides:
  - even with `f = 1`, rotating-leader SMR fails

## 2. Byzantine Broadcast and Consensus Limits

### 2.1 Byzantine Broadcast (BB)
- BB is a single-shot consensus problem.
- Any BB solution can be combined with rotating leaders to solve SMR.
- In that reduction, we also need to detect if the current leader is Byzantine.
- Setting:
  - one of the `n` nodes is the sender
  - sender identity is known to everyone in advance
  - sender may be Byzantine
  - sender has a private input `v*` from some set `V`
- Desired properties:
  - termination: every honest node `i` eventually halts with some output `v_i` in `V`
  - agreement: all honest nodes halt with the same output, even if the sender is Byzantine
  - validity: if the sender is honest, then the common output of the honest nodes equals the sender's private input `v*`
- Relationship to SMR properties:
  - agreement is a safety property like consistency
  - termination + validity are similar in spirit to liveness
- The slides emphasize:
  - termination + validity alone are easy
  - termination + agreement alone are easy
  - getting all three together is the hard part

### 2.2 Reducing SMR to BB
- Suppose `pi` is a BB protocol that:
  - terminates in at most `T` time steps
  - satisfies agreement
  - satisfies validity
- At times `0, T, 2T, ...`:
  - select current leader using round-robin
  - leader builds ordered list `L*` of all not-yet-included transactions it has heard about
  - invoke BB with that leader as sender and `L*` as the sender's private input
  - when BB terminates, each node `i` appends its output `L_i` to its history
- If `pi` tolerates at most `f` Byzantine nodes, then this SMR construction achieves consistency and liveness for the same bound `f`.
- Slight liveness modification:
  - only requests submitted to honest nodes are guaranteed to be eventually included

### 2.3 Simple cross-checking BB protocol for `f = 1`
- Byzantine strategy to worry about:
  - sender sends conflicting messages to different nodes
- Main idea:
  - honest nodes cross-check messages
- Protocol:
  - time step 1:
    - sender sends its private value `v*` and its signature to every non-sender
    - let `m_i` be the signed message sent to non-sender `i`
  - time step 2:
    - each non-sender signs `m_i`
    - it sends the message-signature pair to all other non-senders
    - if an honest non-sender did not receive any message from the sender in step 1, it behaves as if it received the null value `bottom`
  - time step 3:
    - each non-sender applies majority rule over the messages it received from the sender and the other non-senders
    - ties are broken consistently, for example lexicographically
    - sender outputs its private value `v*`
- Proposition in the slides:
  - when `f = 1`, this protocol satisfies termination, agreement, and validity

### 2.4 Why the `f = 1` protocol works
- Termination:
  - every honest node halts after 3 steps
- Agreement, honest sender case:
  - all honest non-senders receive `v*`
  - the Byzantine non-sender cannot forge the sender's signature on a different value
  - it can only cause omission faults
  - therefore all honest non-senders receive at least `n - 2` votes for `v*`
- Agreement, Byzantine sender case:
  - if sender is Byzantine and `f = 1`, then all non-senders are honest
  - by the start of step 3, all non-senders have exactly the same information
  - they therefore compute the same majority outcome, possibly `bottom`
- Validity:
  - only the honest-sender case matters
  - all honest non-senders receive at least `n - 2` votes for `v*`

### 2.5 Why that protocol fails for `f = 2`
- Assume:
  - sender and one non-sender are Byzantine
  - `n` is even and `n >= 4`
  - `V` contains `0` and `1`
- First time step:
  - Byzantine sender sends `0` to one half of honest non-senders
  - Byzantine sender sends `1` to the other half
  - sender also shares both signed messages with the Byzantine non-sender
- Second time step:
  - Byzantine non-sender echoes `0` to the first honest group
  - Byzantine non-sender echoes `1` to the second honest group
  - honest non-senders echo whatever they received from the sender
- Third time step:
  - one honest group sees a majority for `0`
  - the other honest group sees a majority for `1`
  - they output different values
- Result:
  - agreement is violated

### 2.6 Dolev-Strong protocol
- Proposed in 1983 as a BB solution.
- Works for any `f` in the permissioned, PKI, synchronous setting.
- Definition of a convincing message:
  - node `i` is convinced of value `v` at time step `t` if before that time step it receives a message that:
    - references value `v`
    - is signed first by the sender
    - is signed by at least `t - 1` other distinct nodes
- Protocol:
  - time step 0:
    - sender sends `v*` with its signature to all non-senders
    - sender outputs `v*`
  - time steps `t = 1, 2, ..., f + 1`:
    - if a non-sender is convinced of value `v` by message `m` before time step `t`
    - and it was not previously convinced of `v`
    - it signs `m` to get signature `s`
    - it sends `(m, s)` to all other non-senders
  - final output:
    - if a non-sender is convinced of exactly one value `v`, output `v`
    - otherwise output `bottom`
- Theorem in the slides:
  - Dolev-Strong satisfies termination, validity, and agreement for any number of Byzantine nodes `f`

### 2.7 FLM impossibility result
- The slide attributes:
  - originally established by Pease, Shostak, and Lamport in 1980
  - named after Fischer, Lynch, and Merritt (1986), who gave a nice proof
- This result shows the PKI assumption is necessary for Dolev-Strong.
- Setting:
  - synchronous
  - permissioned
  - no PKI
- Statement:
  - if `f >= n / 3`, then there is no Byzantine broadcast protocol satisfying termination, agreement, and validity

### 2.8 Asynchronous network model
- Synchronous model assumptions:
  - shared global clock
  - every message sent at time `t` arrives by `t + 1`
- This is unrealistic for the Internet because of outages and DoS attacks.
- Assuming known bounds on message delay and clock drift again leads to a synchronous model.
- Asynchronous model:
  - no shared global clock
  - no upper bound on message delay
  - every sent message eventually arrives

### 2.9 FLP impossibility theorem
- Named after Fischer, Lynch, and Paterson.
- Applies in the permissioned, PKI, asynchronous setting.
- Byzantine agreement setting:
  - single-shot consensus
  - no sender node
  - node `i` has private input `v_i` in `V`
- Desired properties:
  - termination: every honest node `i` eventually halts with some output `w_i` in `V`
  - agreement: all honest nodes halt with the same output
  - validity: if every honest node starts with the same value `v*`, then every honest node outputs `v*`
- FLP theorem statement:
  - for every `n >= 2`, even with `f = 1`, no deterministic Byzantine agreement protocol satisfies termination, agreement, and validity in the asynchronous model
- Additional notes from the slides:
  - randomized asynchronous BA protocols do exist
  - example given: HoneyBadgerBFT
  - practical blockchain protocols avoid FLP by relaxing the pure asynchronous assumption

### 2.10 Partially synchronous network model
- This model lies between synchronous and asynchronous.
- All nodes share a global clock.
- Message delays may be arbitrary until some unknown time called the global stabilization time (GST).
- After GST, message delays are bounded by a known value `Delta`.
- Delivery model:
  - if message is sent at `t <= GST`, it arrives by `GST + Delta`
  - if message is sent at `t >= GST`, it arrives by `t + Delta`
- Consensus goals in this model:
  - safety properties must always hold, even before GST
  - liveness properties need only eventually hold, possibly only after GST
- Theorem in the slides:
  - there exists a deterministic Byzantine agreement protocol with agreement, validity, and eventual post-GST termination if and only if `f < n / 3`
  - Tendermint and PBFT achieve the "if" direction

### 2.11 The 33 percent threshold
- Reasoning:
  - honest nodes can wait only for messages from `n - f` nodes before acting
  - some of those `n - f` responders may themselves be Byzantine
  - so the honest nodes within those responders must still be a strict majority
- Therefore:
  - `f < (n - f) / 2`
  - equivalently `f < n / 3`
  - equivalently `n >= 3f + 1`
- Special-case proof sketch for `n = 3`, `f = 1`:
  - assume there is a protocol with agreement, validity, and eventual termination
  - let Alice, Bob, Carol be the nodes
  - Bob is Byzantine
  - Alice starts with input `1`
  - Carol starts with input `0`
  - all Alice-Carol messages are delayed
  - Bob sends `1` to Alice and withholds Carol's messages
  - Bob sends `0` to Carol and withholds Alice's messages
  - to satisfy validity and termination, Alice outputs `1` and Carol outputs `0`
  - agreement is violated

### 2.12 CAP principle
- Consistency:
  - all nodes agree on the same history
  - a consistent distributed system looks centralized to the client
- Availability:
  - a client request should eventually be executed
  - example from slides: a distributed database query should eventually return a response
- Partition tolerance:
  - consistency and availability should continue to hold in the presence of a network partition
- CAP principle:
  - no distributed system can have all three properties
  - network partitions are unavoidable in practice
  - protocols must choose between consistency/safety and availability/liveness
- Examples from the slides:
  - Tendermint/PBFT give up liveness during a network partition
  - Bitcoin's heaviest-chain rule gives up consistency because long reorganizations are possible

## 3. Ethereum Blocks

### 3.1 Basic context
- Ethereum launched as a proof-of-work chain in July 2015.
- It transitioned to proof-of-stake in September 2022. This is the Merge.
- Ethereum node components:
  - execution client: executes transactions and updates world state
  - beacon chain client: implements the PoS algorithm that reaches consensus on execution client blocks

### 3.2 Ethereum 1.0 block header
- Block structure:
  - `Block = (Header, Transactions, Uncle Headers)`
- Header fields and sizes:
  - `parentHash`: 32 bytes
  - `ommersHash`: 32 bytes
  - `beneficiary`: 20 bytes
  - `stateRoot`: 32 bytes
  - `transactionsRoot`: 32 bytes
  - `receiptsRoot`: 32 bytes
  - `logsBloom`: 256 bytes
  - `difficulty`: at least 1 byte
  - `number`: at least 1 byte
  - `gasLimit`: at least 1 byte
  - `gasUsed`: at least 1 byte
  - `timestamp`: at most 32 bytes
  - `extraData`: at most 32 bytes
  - `mixHash`: 32 bytes
  - `nonce`: 8 bytes

### 3.3 Uncle blocks / ommers in Ethereum 1.0
- Ethereum 1.0 block can be thought of as:
  - `Block = (Header, Transactions, Uncle Header List)`
- `ommersHash` is the hash of the uncle header list.
- "Ommer" is a gender-neutral term meaning "sibling of parent."
- Problem addressed:
  - low inter-block time leads to a high stale-block rate
  - stale blocks do not contribute to security
- Solution:
  - reward stale-block miners
  - also reward miners who include stale block headers
- Important facts:
  - rewarded stale blocks are called uncles or ommers
  - transactions in uncle blocks are invalid
  - uncle creators receive only a fraction of the block reward
  - they do not receive transaction fees
- Fork resolution:
  - GHOST was proposed by Sompolinsky and Zohar in December 2013
  - Ethereum 1.0 used a simpler version of GHOST
  - Ethereum 2.0 also uses a GHOST variant called LMD GHOST

### 3.4 GHOST protocol
- GHOST is a policy for choosing the main chain in the presence of forks.
- Given a block tree `T`, `GHOST(T)` is the block representing the main chain.
- Mining nodes compute `GHOST(T)` locally and mine on top of it.
- Rule:
  - at each fork, choose the child whose subtree is heaviest
- Pseudocode idea from the slides:
  - start at the genesis block
  - while current block has children
  - move to the child whose subtree has maximum size
  - when there are no children, return the current block

### 3.5 GHOST example
- Suppose an attacker secretly builds chain `1A, 2A, ..., 6A`.
- All other blocks are mined by honest miners.
- Honest mining power is spread across several forks.
- Longest-chain rule chooses:
  - `0, 1B, 2D, 3F, 4C, 5B`
  - that chain is shorter than the attacker's private chain
- GHOST chooses:
  - `0, 1B, 2C, 3D, 4B`
- This illustrates why heaviest-subtree can be preferable to plain longest-chain.

### 3.6 Eth2 execution client block header
- The slides still write:
  - `Block = (Header, Transactions, Uncle Headers)`
- Header fields in the execution client block:
  - `parentHash`: 32 bytes
  - `ommersHash`: 32 bytes
  - `beneficiary`: 20 bytes
  - `stateRoot`: 32 bytes
  - `transactionsRoot`: 32 bytes
  - `receiptsRoot`: 32 bytes
  - `logsBloom`: 256 bytes
  - `difficulty`: 1 byte
  - `number`: at least 1 byte
  - `gasLimit`: at least 1 byte
  - `gasUsed`: at least 1 byte
  - `timestamp`: at most 32 bytes
  - `extraData`: at most 32 bytes
  - `prevRandao`: 32 bytes
  - `nonce`: 8 bytes
  - `baseFeePerGas`: at least 1 byte

### 3.7 Fields deprecated or changed after the Merge
- `ommersHash` becomes the hash of an empty list.
- `difficulty` is set to zero.
- `nonce` is set to 8 zero bytes.
- `mixHash` is replaced with `prevRandao`.
- `RANDAO` is a pseudorandom value generated by validators in the PoS algorithm.

### 3.8 Meaning of key execution-header fields
- `parentHash`:
  - Keccak-256 hash of the parent block header
- `beneficiary`:
  - destination address of the block reward and transaction fees
- `stateRoot`:
  - root hash of the world-state trie after all transactions in the block are applied
- `transactionsRoot`:
  - root hash of the trie populated with all transactions in the block
- `number`:
  - number of ancestor blocks
- `timestamp`:
  - Unix time at block creation
- `extraData`:
  - arbitrary data
  - validators identify themselves there

### 3.9 `receiptsRoot`
- `receiptsRoot` is the root hash of the transaction receipts trie.
- A transaction receipt contains logs emitted by smart contracts.
- Smart contracts write logs using events.
- Example event from the slides:

```solidity
event Transfer(address indexed from, address indexed to, uint256 value);
```

### 3.10 Transaction receipts trie
- Implemented as an Ethereum Merkle Patricia Trie.
- Each leaf node contains one transaction receipt.
- Key:
  - RLP encoding of the transaction index within the block
- Value:
  - RLP-encoded transaction receipt
- Receipt structure from the slides:
  - `receipt = [status, cumulativeGasUsed, logsBloom, logs]`
- Inside it:
  - `logsBloom` is the transaction Bloom filter
  - `logs = [log0, log1, ...]`
- Log structure:
  - `[address, [topic0, topic1, ..., topic3], data]`
- Meaning of log components:
  - `address`: contract address that emitted the log
  - `topic0`: Keccak hash of the event signature
  - `topic1` to `topic3`: indexed parameters
- Transfer-event example:
  - `topic0 = keccak256("Transfer(address,address,uint256)")`
  - `topic1 = sender address`
  - `topic2 = receiver address`
  - `data = value`
- The address and topics are used to create the Bloom filter.

### 3.11 `logsBloom`
- Bloom filter is a probabilistic data structure for membership queries.
- Each transaction receipt has a Bloom filter of addresses and topics.
- Block header `logsBloom` is the bitwise OR of all transaction receipt Bloom filters.
- Construction detail from the slides:
  - Keccak hash of the logger address and indexed topics is used to set 3 bits out of 2048
- Use case:
  - light clients can efficiently retrieve only transactions of interest

### 3.12 Fee-related fields
- `gasUsed`:
  - total gas used by all transactions in the block
- `gasLimit`:
  - maximum gas usable by the block
  - the slide states it is currently 60 million
- `baseFeePerGas`:
  - minimum required transaction fee per gas unit
  - burned by the protocol
  - updated each block depending on how far `gasUsed` is from the target limit of 30 million

### 3.13 Base fee calculation (EIP-1559)
- Introduced in EIP-1559 and included in the London hard fork in August 2021.
- Formulas from the slides:

```text
gasTarget = gasLimit / 2
delta = ((gasUsed - gasTarget) / (4 * gasLimit)) * baseFeePerGas
baseFeePerGas_new = baseFeePerGas + delta
```

- Before EIP-1559:
  - gas prices worked like a first-price auction
  - users had to guess the gas price needed for inclusion
- After EIP-1559:
  - base fee indicates demand for blockspace
  - users can additionally pay a priority fee (tip)

## 4. Ethereum Virtual Machine (EVM)

### 4.1 What the EVM is
- The EVM is a stack-based computer that executes smart contract instructions.
- Smart contracts are compiled into EVM opcodes.
- It is a stack-based architecture with 32-byte words.
- Contract code is stored in a virtual ROM.
- Stack and memory are volatile:
  - they do not persist across transactions
- Storage is persistent:
  - it is the smart contract's long-term memory

### 4.2 EVM resources
- Stack:
  - maximum size is 1024 words
- Memory:
  - a word-addressed byte array
  - theoretical maximum size is `2^256` bytes
  - gas cost increases quadratically with memory size
- Account storage:
  - key-value map from 32-byte words to 32-byte words
  - persists across transactions
  - current contract storage is accessed by `SLOAD` and `SSTORE`
  - storage of other contracts cannot be read
- Code of another contract can be read with `EXTCODECOPY`.
- Transaction calldata can be read with:
  - `CALLDATALOAD`
  - `CALLDATACOPY`

### 4.3 Opcodes and gas
- EVM opcodes are 1 byte each.
- The deck points to the full list at `https://www.evm.codes/`.
- Example gas costs:
  - `ADD`, `SUB`: 3 gas
  - `MUL`, `DIV`: 5 gas
  - `MLOAD`, `MSTORE`: `3 + memory expansion cost`
- Opcodes touching storage or world state cost more.
- Specific numbers from the slides:
  - `SLOAD`
    - 2100 gas for cold keys
    - 100 gas for warm keys
  - `CALL`
    - 2600 gas for cold addresses
    - 100 gas for warm addresses
  - `BALANCE`
    - 2600 gas for cold addresses
    - 100 gas for warm addresses
  - `CREATE`
    - minimum gas cost 32000

### 4.4 Memory expansion gas cost
- Some opcodes access memory using an offset.
- Example: `MSTORE`
  - consumes the top two stack words
  - top stack word is the memory offset to write to
  - next stack word is written at that offset
- If the requested offset is beyond previously accessed memory, memory expansion cost is charged.
- Memory expands in 32-byte increments.
- Formula from the slides:

```text
memory_size_word = (memory_byte_size + 31) / 32
memory_cost = (memory_size_word^2) / 512 + 3 * memory_size_word
```

### 4.5 Notable gas costs
- Every transaction has an initial cost of 21000 gas.
- It may cost more if it does more than a simple Ether transfer.
- Calldata gas:
  - 4 gas per zero byte
  - 16 gas per non-zero byte
- Why calldata is important:
  - it exists only during the current transaction
  - storage persists across transactions and is more expensive
  - cheap calldata is crucial for Layer 2 designs on Ethereum
- `KECCAK256` gas cost:
  - `30 + 6 * (number of hashed words)`

### 4.6 Precompiles
- The EVM provides advanced operations via precompiled contracts.
- These live at fixed addresses.
- The deck points to `https://www.evm.codes/precompiled`.
- Example:
  - `ecPairing`
  - address `0x08`
  - computes an elliptic curve pairing
  - used for verifying Groth16 SNARK proofs
  - costs 45000 gas

## 5. Solidity Tutorial

### 5.1 Basic language facts
- Solidity is a programming language for implementing smart contracts on Ethereum.
- It is statically typed.
- Its syntax is JavaScript-like.
- Example contract from the slides:

```solidity
pragma solidity >= 0.4.16 < 0.9.0;

contract SimpleStorage {
    uint storedData;

    function set(uint x) public {
        storedData = x;
    }

    function get() public view returns (uint) {
        return storedData;
    }
}
```

- `public` means the function can be invoked using a transaction.
- `view` means the function does not change world state.

### 5.2 Variable types
- Solidity variables are of three kinds:
  - local:
    - declared inside a function
    - not stored in world state
  - state:
    - declared outside functions
    - stored in world state
  - special:
    - always exist in the global namespace
    - provide information about blocks or transactions
- Example special variables from the deck:
  - `block.number`
  - `msg.sender`

### 5.3 Primitive data types
- `bool`
- `uint`
  - in the slides, plain `uint` means unsigned 256-bit integer
- `int`
  - in the slides, plain `int` means signed 256-bit integer
- `address`
- fixed-size byte arrays from `bytes1` to `bytes32`
- `string`

### 5.4 Constants and immutables
- Constant variables cannot be modified.
- Convention shown in the slides:
  - use uppercase names for constants
- Constants save gas because their values can be hardcoded.
- Immutable variables:
  - can be initialized in the constructor
  - cannot be modified after deployment
- Constructor fact:
  - constructor runs only during contract deployment

### 5.5 Mappings
- Syntax:

```solidity
mapping(keyType => valueType)
```

- Purpose:
  - store key-value pairs
- Properties from the slides:
  - mapping lookup always returns a value
  - if the key has never been set, it returns the default value
  - deleting a mapping entry resets it to the default value
- Type rules:
  - `keyType` cannot be a reference type
    - arrays
    - structs
    - mappings
  - `valueType` can be any type, including another mapping

### 5.6 Nested mappings
- Example shape:

```solidity
mapping(address => mapping(uint => bool)) public nested;
```

- Access syntax:

```solidity
nested[key1][key2]
```

- Important point:
  - values can be accessed even if the nested mapping was never explicitly initialized

### 5.7 Arrays
- Syntax:
  - `type[]`
- Arrays may be:
  - dynamic
  - fixed-size
- Examples from the slides:
  - `uint[] public arr;`
  - `uint[] public arr2 = [1, 2, 3];`
  - `uint[10] public myFixedSizeArr;`
- Operations shown:
  - read with indexing
  - append with `push`
  - remove last element with `pop`

### 5.8 Function inputs and outputs
- Functions can return multiple values.
- Mappings cannot be public-function inputs or outputs.
- Arrays can be used as public-function inputs and outputs.
- `pure` functions:
  - do not read state
  - do not modify state
- `memory` keyword on array values:
  - specifies the data location

### 5.9 Data locations for reference types
- Reference types:
  - arrays
  - mappings
  - structs
- Data locations:
  - `memory`
  - `storage`
  - `calldata`
- In function inputs/outputs, reference-type data locations are mandatory.
- `calldata`:
  - read-only
  - cheaper when usable

### 5.10 Structs
- Example from the slides:

```solidity
struct Todo {
    string text;
    bool completed;
}
```

- Example pattern:
  - store an array of `Todo` structs
  - create new todo by pushing a struct
  - get a struct by returning `Todo memory`
  - use `Todo storage todo = todos[_index];` for in-place updates
- Update example shown:
  - toggle the `completed` field

### 5.11 Control flow
- `if / else if / else`
- `for`
- `while`

### 5.12 Events
- Event declaration example:

```solidity
event Log(address indexed sender, string message);
event AnotherLog();
```

- Facts from the slides:
  - up to 3 parameters can be indexed
  - emit with `emit`
  - events let applications read only relevant transactions
  - indexed parameters can be used for event queries
  - the contract address, event signature, and indexed parameters contribute to Bloom filter bits

### 5.13 Event example: `Set`
- Example contract emits:

```solidity
event Set(address indexed setter, uint value);
```

- It is emitted whenever `set(uint x)` is called.
- To listen for events, the slides say we need:
  - an Ethereum full node, or
  - an RPC provider
- The slides use `ethers.js` for event listening from JavaScript.

### 5.14 Listening for events with `ethers.js`
- Imports shown:
  - `AlchemyProvider`
  - `ethers`
  - `dotenv`
- Flow shown:
  - read API key from `.env`
  - construct `ethers.AlchemyProvider("sepolia", process.env.API_KEY)`
  - define contract address
  - define ABI
  - create contract object with provider
  - attach listener:

```javascript
ssContract.on("Set", (from, value, event) => {
    console.log(`${from} set ${value}`);
});
```

- Notes directly stated in the slides:
  - this script uses Alchemy as the RPC provider
  - `abi` contains the contract's application binary interface
  - the contract object connects to the deployed contract through Alchemy
  - `.on("Set", ...)` registers the event listener

### 5.15 `require` and `assert`
- `require` is used to validate inputs and preconditions before execution.
- Syntax:

```solidity
require(bool condition, string memory message)
```

- The slides show an overflow check:
  - compute `oldBalance`
  - compute `newBalance = accBalance + _amount`
  - `require(newBalance >= oldBalance, "Overflow");`
- `assert(bool condition)`:
  - used for conditions that should never be false
- Both `require` and `assert`:
  - abort execution if the condition is false
  - revert state changes

### 5.16 Function modifiers
- Modifiers let code run before and/or after a function body.
- Example:
  - store owner in constructor
  - define `onlyOwner`
  - check `msg.sender == owner`
  - `_` marks where the rest of the function executes
- Example usage:

```solidity
function changeOwner(address _newOwner) public onlyOwner
```

### 5.17 Inheritance
- Use `is` for inheritance.
- Base function must be marked `virtual` to be overridden.
- Child implementation must be marked `override`.

### 5.18 Multiple inheritance
- Solidity supports multiple inheritance.
- Parent contracts are searched from right to left.
- Immediate parent functions can be called with `super`.
- Example from the slides:
  - `contract D is B, C`
  - `super.foo()` resolves to the right-most parent implementation if appropriate

### 5.19 Inherited state
- State variables cannot be overridden directly.
- To change inherited state, reinitialize it in the child constructor.
- Example from the slides:
  - base has `string public name = "Contract A";`
  - child constructor sets `name = "Contract B";`

### 5.20 Function annotations / visibility
- `public`
  - callable by contracts and EOAs
- `private`
  - callable only inside the contract that defines it
- `internal`
  - callable inside the defining contract and child contracts
- `external`
  - callable by other contracts and EOAs

### 5.21 `payable`
- Payable functions and payable addresses can receive Ether.
- The slides also note that a payable address can send Ether via `transfer` or `send`.
- The example marks owner as:

```solidity
address payable public owner;
```

- Constructor casts sender to payable:

```solidity
owner = payable(msg.sender);
```

- Deposit pattern:
  - `function deposit() public payable {}`
- Withdraw pattern shown:
  - get `address(this).balance`
  - send all Ether with low-level call
  - require success

### 5.22 Calling other contracts by contract type
- Example from the slides:

```solidity
Callee callee = Callee(_addr);
callee.setX(_x);
```

- This requires the `Callee` contract type to be available in the caller's scope.
- Limitations noted in the slides:
  - `Callee` may change due to optimizations or new features
  - any change to `Callee` requires changing `Caller`
  - that implies redeploying `Caller`
- Suggested workarounds in the slides:
  - interfaces
  - low-level `call`

### 5.23 Low-level `call`
- `call` can be used to invoke functions in other contracts.
- Especially useful when the target contract source is not available in the current contract.
- Requirement:
  - the function signature must still be known
- General syntax from the slides:

```solidity
<address>.call{
  value: ethAmount,
  gas: gasLimit
}(abi.encodeWithSignature(functionSignature, arguments))
```

- Meaning of fields:
  - `value`: Ether sent with the call
  - `gas`: maximum gas for the call
  - `abi.encodeWithSignature(...)`: serializes the function signature and arguments into bytes
- Example from the slides:

```solidity
(bool success, bytes memory data) = _addr.call{
    value: msg.value,
    gas: 5000
}(abi.encodeWithSignature("foo(string,uint256)", "hi", 123));
```

### 5.24 Interfaces
- Contracts can interact through interfaces.
- Interface-usage example from the slides:
  - `ICounter(_counter).increment();`
  - `return ICounter(_counter).count();`
- Interface facts from the slides:
  - only declarations, no implementations
  - no state variables
  - all functions must be `external`
  - interfaces can inherit from other interfaces
- Interfaces can declare:
  - functions
  - events
  - custom errors
- Examples named in the slides:
  - ERC-20 token standard
  - ERC-721 non-fungible token standard

### 5.25 `receive` and `fallback`
- Warning from the slides:
  - when Ether is sent to a contract, it can get lost forever
- `receive`:
  - contract can define a receive function to move received Ether to an EOA account
- `fallback` is called when:
  - a function that does not exist is called
  - Ether is sent directly but `receive` does not exist
  - Ether is sent directly, `receive` exists, but `msg.data` is not empty
- Example fallback from the slides:

```solidity
fallback(bytes calldata data) payable returns (bytes memory) {
    (_, bytes memory res) = target.call{value: msg.value}(data);
    return res;
}
```

- This is a forwarding / proxy-style pattern.

## 6. Re-Entrancy and Token Contracts

### 6.1 The DAO story
- DAO = decentralized autonomous organization.
- In the slide definition:
  - a smart contract for coordination
  - people deposit Ether and receive another token
  - DAO token can be used to vote on proposals
- Historical facts given:
  - in 2016, a DAO collected 3.54 million Ether
  - slide says this was about 150 million USD
  - less than 3 months after launch, a hacker drained ETH using a re-entrancy attack
  - Ethereum was forked to fix the bug
  - Ethereum Classic is the chain where DAO funds were lost
- DAO contract supported two main actions:
  - deposit Ether
  - withdraw previously deposited Ether

### 6.2 Vulnerable DAO pattern
- Simplified vulnerable `withdraw()` flow:
  - check user balance
  - store `bal = balances[msg.sender]`
  - send Ether with:

```solidity
(bool sent, ) = msg.sender.call{value: bal}("");
```

  - only after the external call, set:

```solidity
balances[msg.sender] = 0;
```

- Problem:
  - the external call happens before the balance reset
  - attacker can re-enter through fallback before state is updated

### 6.3 Attacker contract pattern
- The attack contract:
  - stores DAO interface address
  - seeds DAO with at least 1 Ether
  - calls `dao.deposit{value: msg.value}();`
  - then calls `dao.withdraw();`
- In attack fallback:

```solidity
if (address(dao).balance >= 1 ether) {
    dao.withdraw();
}
```

- This repeatedly re-enters while the DAO still has enough Ether.

### 6.4 Fixing re-entrancy

#### Fix A: checks-effects-interactions
- Reset user balance before sending Ether:

```solidity
balances[msg.sender] = 0;
(bool sent, ) = msg.sender.call{value: bal}("");
require(sent, "Failed to withdraw sender's balance");
```

#### Fix B: re-entrancy lock
- Use a modifier with a `locked` boolean:

```solidity
modifier noReentrancy() {
    require(!locked, "No reentrancy");
    locked = true;
    _;
    locked = false;
}
```

- Apply it to `withdraw()`.

### 6.5 ERC-20 token standard
- ERC-20 is a standard interface for fungible tokens on Ethereum.
- Slide reference URL:
  - `https://eips.ethereum.org/EIPS/eip-20`
- The tutorial uses OpenZeppelin's ERC-20 implementation.
- Example shown:

```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract EE465Token is ERC20 {
    uint constant _initial_supply = 100 * (10**18);

    constructor() ERC20("EE465 Token", "CBT") {
        _mint(msg.sender, _initial_supply);
    }
}
```

- Slides note:
  - OpenZeppelin provides open-source implementations of token standards

### 6.6 ERC-20 interface
- Events:
  - `Transfer(address indexed from, address indexed to, uint256 value)`
  - `Approval(address indexed owner, address indexed spender, uint256 value)`
- Functions:
  - `totalSupply() external view returns (uint256)`
  - `balanceOf(address account) external view returns (uint256)`
  - `transfer(address to, uint256 value) external returns (bool)`
  - `allowance(address owner, address spender) external view returns (uint256)`
  - `approve(address spender, uint256 value) external returns (bool)`
  - `transferFrom(address from, address to, uint256 value) external returns (bool)`

### 6.7 Partial ERC-20 implementation facts from the slides
- Storage variables shown:

```solidity
uint256 public totalSupply;
mapping(address => uint256) public balanceOf;
mapping(address => mapping(address => uint256)) public allowance;
string public name;
string public symbol;
```

- Constructor:

```solidity
constructor(string memory _name, string memory _symbol) {
    name = _name;
    symbol = _symbol;
}
```

- `_mint`:

```solidity
function _mint(address to, uint256 amount) internal {
    balanceOf[to] += amount;
    totalSupply += amount;
    emit Transfer(address(0), to, amount);
}
```

- `_mint` can be used to set the initial supply.
- `transfer` implementation points shown:
  - require sender balance is enough
  - subtract from sender
  - add to recipient
  - emit `Transfer`
  - return `true`
- `approve` implementation points shown:
  - set allowance
  - emit `Approval`
  - return `true`
- `transferFrom` implementation points shown:
  - require allowance is enough
  - decrement allowance
  - decrement sender balance
  - increment recipient balance
  - emit `Transfer`
  - return `true`

### 6.8 Non-fungible tokens (NFTs)
- ERC-721 is the non-fungible token standard.
- Example implementation link in the slides:
  - `https://solidity-by-example.org/app/erc721/`
- Slide wording:
  - NFTs are simply counters in an ERC721 contract
- Example ownership mapping:

```solidity
mapping(uint256 => address) internal _ownerOf;
```

- Example `_mint`:

```solidity
function _mint(address to, uint256 id) internal {
    require(to != address(0), "mint to zero address");
    require(_ownerOf[id] == address(0), "already minted");

    _balanceOf[to]++;
    _ownerOf[id] = to;

    emit Transfer(address(0), to, id);
}
```

- Important NFT fact from the slides:
  - NFT images are not stored in the contract
  - only links are stored
- Metadata interface shown:
  - `name()`
  - `symbol()`
  - `tokenURI(uint256 _tokenId)`
- The slide notes:
  - `tokenURI` typically points to a JSON file containing metadata

## 7. Tornado Cash

### 7.1 Motivation
- Scenario in the slides:
  - you hold 100 ETH in a self-custodial wallet
  - you pay 1 ETH hotel rent
  - the recipient can see your address still has 99 ETH
  - that leaks sensitive wealth information
- Option A from the slides:
  - use an exchange wallet to pay
  - drawbacks:
    - exchange hacks can lose funds
    - customer data can leak
- Option B from the slides:
  - send 1 ETH from the main address to a fresh address
  - use the fresh address to pay
  - drawback:
    - if you later fund another fresh address from the same main wallet, the linkage reappears
- Tornado Cash is presented as a better version of Option B.
- It is a mixer implemented as an Ethereum smart contract.

### 7.2 Tornado Cash overview
- The slide specifically refers to the pre-Nova version.
- Example picture flow:
  - Alice deposits 1 ETH
  - Bob deposits 1 ETH
  - Carol deposits 1 ETH
  - funds are later withdrawn to fresh addresses
- Desired functionality:
  - soundness
    - only past depositors should be able to withdraw
    - no double withdrawal
  - privacy
    - a withdrawal should not be linkable to a specific past deposit

### 7.3 Deposit workflow
- Screenshot-only slides show the user flow:
  - choose amount and chain
  - connect wallet
  - save note
  - deposit

### 7.4 Deposit steps
- Tornado note anatomy in the slides:
  - header
  - 31-byte nullifier
  - 31-byte secret
- The slide example note begins with:

```text
tornado-eth-0.1-5-0x...
```

- Important facts:
  - the nullifier and secret together give 62 bytes
  - those 62 bytes are randomly generated on the user's computer
- Commitment:
  - a Pedersen hash of the 62 bytes is computed and submitted to the contract
- The slides write Pedersen hash as:

```text
Pedersen hash of bitstring b1 b2 ... bn = g1^b1 g2^b2 ... gn^bn
```

- Contract checks the commitment is fresh:

```solidity
mapping(bytes32 => bool) public commitments;
require(!commitments[_commitment], "The commitment has been submitted");
```

- Then the contract inserts `_commitment` into a Merkle tree:

```solidity
uint32 insertedIndex = _insert(_commitment);
```

- Merkle-tree facts:
  - 20 levels
  - `insertedIndex` is the new leaf index
  - no leaf deletions
  - therefore maximum number of deposits is `2^20`
- Contract then:
  - records `commitments[_commitment] = true;`
  - checks the ETH sent matches the denomination:

```solidity
require(msg.value == denomination, "Please send 1 ETH with transaction");
```

  - emits:

```solidity
emit Deposit(_commitment, insertedIndex, block.timestamp);
```

### 7.5 Withdrawal workflow
- Screenshot-only slides show the withdrawal flow:
  - enter note string and recipient address
  - choose relayer
  - or choose a wallet if you already have an unlinkable address with ETH
  - generate proof
  - confirm withdrawal

### 7.6 Withdrawal steps
- Withdraw function shape shown in the slides:

```solidity
function withdraw(
  bytes calldata _proof,
  bytes32 _root,
  bytes32 _nullifierHash,
  address payable _recipient,
  address payable _relayer,
  uint256 _fee
)
```

- `_proof` is a SNARK proof for the statement:
  - I know the secret and nullifier for a commitment included in the Merkle tree with root `_root`
  - `_nullifierHash` is the Pedersen hash of that commitment's nullifier
- Contract checks `_nullifierHash` has not been seen:

```solidity
mapping(bytes32 => bool) public nullifierHashes;
require(!nullifierHashes[_nullifierHash], "Note already spent");
```

- This prevents double withdrawal.
- Contract checks the root is recognized:

```solidity
require(isKnownRoot(_root), "Cannot find your merkle root");
```

- The slide says `_root` must be one of the last 100 Merkle roots.
- Contract verifies the SNARK proof on-chain:

```solidity
require(
  verifier.verifyProof(_proof, [uint256(_root), uint256(_nullifierHash), ...]),
  "Invalid withdraw proof"
);
```

- After successful verification:
  - store `nullifierHashes[_nullifierHash] = true;`
  - send `denomination - _fee` to recipient
  - send `_fee` to relayer
- The slides also state:
  - the SNARK proof "signs" `_recipient`, `_relayer`, and `_fee` to prevent tampering
  - the verifier contract is generated using the `circom` compiler
- One slide is an image labeled `withdraw.circom`, indicating the circuit behind the withdraw proof

### 7.7 OFAC sanctions slide
- On August 8, 2022, the US Office of Foreign Assets Control put Tornado Cash addresses on a sanctions list.
- US residents and businesses cannot interact with sanctioned entities.
- Allegations mentioned:
  - facilitating money laundering by ransomware operators
  - facilitating laundering by smart-contract attackers
- GitHub actions mentioned:
  - source repositories removed
  - three contributor accounts suspended
- Later developments in the slides:
  - due to efforts by Prof. Matthew Green and EFF, OFAC allowed use of the code for educational purposes
  - GitHub repositories and accounts were restored in 2023
  - developer Alexey Pertsev:
    - arrested in the Netherlands in August 2022
    - sentenced to 64 months in May 2024
    - released in February 2025
    - working on appeal
  - developer Roman Storm:
    - arrested in the US on August 23, 2023
    - later released on bail
    - case still ongoing

## 8. Quick Formula and Fact Dump

### Consensus
- SMR requirements:
  - consistency
  - liveness
- BB requirements:
  - termination
  - agreement
  - validity
- Dolev-Strong convincing message at time `t`:
  - references `v`
  - first signed by sender
  - signed by at least `t - 1` other distinct nodes
- Partial synchrony result:
  - deterministic BA with agreement + validity + eventual termination exists iff `f < n / 3`
- Threshold derivation:

```text
f < (n - f) / 2  =>  f < n / 3  =>  n >= 3f + 1
```

### Ethereum blocks and EVM
- Eth2 header changes:
  - `ommersHash` = hash of empty list
  - `difficulty = 0`
  - `nonce = 8 zero bytes`
  - `mixHash` replaced by `prevRandao`
- Receipt:

```text
receipt = [status, cumulativeGasUsed, logsBloom, logs]
```

- Log:

```text
[address, [topic0, topic1, topic2, topic3], data]
```

- `topic0` for ERC-20 transfer:

```text
keccak256("Transfer(address,address,uint256)")
```

- Base fee:

```text
gasTarget = gasLimit / 2
delta = ((gasUsed - gasTarget) / (4 * gasLimit)) * baseFeePerGas
baseFeePerGas_new = baseFeePerGas + delta
```

- Memory expansion:

```text
memory_size_word = (memory_byte_size + 31) / 32
memory_cost = (memory_size_word^2) / 512 + 3 * memory_size_word
```

- Gas numbers to remember:
  - transaction base cost: 21000
  - `ADD`, `SUB`: 3
  - `MUL`, `DIV`: 5
  - `MLOAD`, `MSTORE`: `3 + memory expansion`
  - `SLOAD`: 2100 cold, 100 warm
  - `CALL`: 2600 cold, 100 warm
  - `BALANCE`: 2600 cold, 100 warm
  - `CREATE`: minimum 32000
  - calldata: 4 per zero byte, 16 per non-zero byte
  - `KECCAK256`: `30 + 6 per word`
  - precompile `ecPairing` at `0x08`: 45000

### Solidity and Tornado Cash
- Data locations:
  - `memory`
  - `storage`
  - `calldata`
- Visibility:
  - `public`
  - `private`
  - `internal`
  - `external`
- Re-entrancy fix:
  - update state before external call
  - or use lock modifier
- Tornado deposit:
  - note contains 31-byte nullifier + 31-byte secret
  - commitment = Pedersen hash of those 62 random bytes
  - tree depth 20
  - maximum deposits `2^20`
- Tornado withdrawal:
  - prove knowledge of `(secret, nullifier)` for commitment in known Merkle root
  - prevent double spend with `nullifierHash`
  - accepted root must be among last 100 roots

## 9. References Listed in the Slides

### 9.1 Consensus references
- Foundations of Blockchains video lectures by Tim Roughgarden
- Notes of lectures 1 to 6 from the 2021 Foundations of Blockchains course:
  - `https://timroughgarden.github.io/fob21/l/l1.pdf`
  - `https://timroughgarden.github.io/fob21/l/l2.pdf`
  - `https://timroughgarden.github.io/fob21/l/l3.pdf`
  - `https://timroughgarden.github.io/fob21/l/l4-5.pdf`
  - `https://timroughgarden.github.io/fob21/l/l6.pdf`
- M. Pease, R. Shostak, and L. Lamport, "Reaching agreement in the presence of faults," Journal of the ACM, 1980
- M. J. Fischer, N. A. Lynch, and M. Merritt, "Easy impossibility proofs for distributed consensus problems," Distributed Computing, 1986
- M. J. Fischer, N. A. Lynch, and M. S. Paterson, "Impossibility of distributed consensus with one faulty process," Journal of the ACM, 1985
- Blue eyes puzzle:
  - `https://www.explainxkcd.com/wiki/index.php/Blue_Eyes`
- HoneyBadgerBFT:
  - `https://eprint.iacr.org/2016/199`

### 9.2 Ethereum Blocks references
- Ethereum yellow paper:
  - `https://ethereum.github.io/yellowpaper/paper.pdf`
- GHOST paper:
  - `https://eprint.iacr.org/2013/881`
- Ethereum blog post on the Merge and app layer:
  - `https://blog.ethereum.org/2021/11/29/how-the-merge-impacts-app-layer`
- Solidity events and logs
- Upgrading Ethereum book:
  - `https://eth2book.info/`
- An Economic Analysis of EIP-1559:
  - `https://timroughgarden.org/papers/eip1559.pdf`

### 9.3 EVM references
- Ethereum yellow paper:
  - `https://ethereum.github.io/yellowpaper/paper.pdf`
- EVM opcodes:
  - `https://www.evm.codes/`
- EVM precompiles:
  - `https://www.evm.codes/precompiled`

### 9.4 Solidity references
- Solidity documentation:
  - `https://docs.soliditylang.org/`
- Solidity by Example:
  - `https://solidity-by-example.org/`
- Remix IDE:
  - `https://remix.ethereum.org`
- Events documentation:
  - `https://docs.soliditylang.org/en/latest/contracts.html#events`
- ABI spec:
  - `https://docs.soliditylang.org/en/latest/abi-spec.html`
- ethers.js documentation:
  - `https://docs.ethers.org/v6/`
- Re-entrancy attack
- ERC-20 token standard
- ERC-721 non-fungible token standard

### 9.5 Tornado Cash references
- Tornado Cash app:
  - `https://tornadoeth.cash/`
- Tornado Cash docs:
  - `https://docs.tornadoeth.cash/`
- Circom docs:
  - `https://docs.circom.io/`
- Tornado Cash core repo:
  - `https://github.com/tornadocash/tornado-core`
- EFF article on OFAC sanctions
- EFF update in April 2023

#include "cache.h"
#include "uncore.h"


#define maxRRPV 3
#define NUM_POLICY 2
#define SDM_SIZE 32
#define TOTAL_SDM_SETS NUM_CPUS *NUM_POLICY *SDM_SIZE
#define BIP_MAX 32
#define PSEL_WIDTH 10
#define PSEL_MAX ((1 << PSEL_WIDTH) - 1)
#define PSEL_THRS PSEL_MAX / 2

uint64_t num_accesses=0;
uint64_t num_future_accesses=0;

uint32_t rrpv[LLC_SET][LLC_WAY], bip_counter = 0, PSEL[NUM_CPUS];
unsigned rand_sets[TOTAL_SDM_SETS];

void CACHE::llc_initialize_replacement() {
  if(irreg_data_base<0){
    cout << "Initialize DRRIP state for LLC" << endl;

    for (int i = 0; i < LLC_SET; i++) {
        for (int j = 0; j < LLC_WAY; j++)
        rrpv[i][j] = maxRRPV;
    }

    // randomly selected sampler sets
    // srand(time(NULL));
    unsigned long rand_seed = 1;
    unsigned long max_rand = 1048576;
    uint32_t my_set = LLC_SET;
    int do_again = 0;
    for (int i = 0; i < TOTAL_SDM_SETS; i++) {
        do {
        do_again = 0;
        rand_seed = rand_seed * 1103515245 + 12345;
        rand_sets[i] = ((unsigned)((rand_seed / 65536) % max_rand)) % my_set;
        // printf("Assign rand_sets[%d]: %u  LLC: %u\n", i, rand_sets[i], my_set);
        for (int j = 0; j < i; j++) {
            if (rand_sets[i] == rand_sets[j]) {
            do_again = 1;
            break;
            }
        }
        } while (do_again);
        // printf("rand_sets[%d]: %d\n", i, rand_sets[i]);
    }

    for (int i = 0; i < NUM_CPUS; i++)
        PSEL[i] = 0;
  }
}

int is_it_leader(uint32_t cpu, uint32_t set) {
  uint32_t start = cpu * NUM_POLICY * SDM_SIZE,
           end = start + NUM_POLICY * SDM_SIZE;

  for (uint32_t i = start; i < end; i++)
    if (rand_sets[i] == set)
      return ((i - start) / SDM_SIZE);

  return -1;
}

uint64_t popt_pa_to_va(uint64_t full_addr){
    uint64_t vfull_addr; // Inverse check of virtual address as base and bound are virtual
    map<uint64_t, uint64_t>::iterator ppage_check = inverse_table.find(
        full_addr >> LOG2_PAGE_SIZE);
    if (ppage_check == inverse_table.end()) {
    cout << "Inverse Mapping Failed! cache victim address: "<<full_addr<< endl;
        assert(0);
    }
    vfull_addr = (ppage_check->second) << LOG2_PAGE_SIZE;
    vfull_addr |=(full_addr & ((1 << LOG2_PAGE_SIZE) - 1));
    return vfull_addr;
}

// called on every cache hit and cache fill
void CACHE::llc_update_replacement_state(uint32_t cpu, uint32_t set,
                                         uint32_t way, uint64_t full_addr,
                                         uint64_t ip, uint64_t victim_addr,
                                         uint32_t type, uint8_t hit) {
  // do not update replacement state for writebacks

  if (irreg_data_base < 0){
    if (type == WRITEBACK) {
        rrpv[set][way] = maxRRPV - 1;
        return;
    }

    // cache hit
    if (hit) {
        rrpv[set][way] = 0; // for cache hit, DRRIP always promotes a cache line to
                            // the MRU position
        return;
    }

    // cache miss
    int leader = is_it_leader(cpu, set);

    if (leader == -1) {            // follower sets
        if (PSEL[cpu] > PSEL_THRS) { // follow BIP
        rrpv[set][way] = maxRRPV;

        bip_counter++;
        if (bip_counter == BIP_MAX)
            bip_counter = 0;
        if (bip_counter == 0)
            rrpv[set][way] = maxRRPV - 1;
        } else // follow SRRIP
        rrpv[set][way] = maxRRPV - 1;

    } else if (leader == 0) { // leader 0: BIP
        if (PSEL[cpu] > 0)
        PSEL[cpu]--;
        rrpv[set][way] = maxRRPV;

        bip_counter++;
        if (bip_counter == BIP_MAX)
        bip_counter = 0;
        if (bip_counter == 0)
        rrpv[set][way] = maxRRPV - 1;

    } else if (leader == 1) { // leader 1: SRRIP
        if (PSEL[cpu] < PSEL_MAX)
        PSEL[cpu]++;
        rrpv[set][way] = maxRRPV - 1;

    } else // WE SHOULD NOT REACH HERE
        assert(0);
  } else{
      num_future_accesses++;
      uint64_t vfull_addr = popt_pa_to_va(full_addr);
      if ((uncore.LLC.irreg_data_base<=vfull_addr) && (vfull_addr<uncore.LLC.irreg_data_bound)) {
          num_accesses++;
      }
  }
}

uint8_t LLC_MSB_MASK = (1<<7);
uint8_t LLC_NO_MSB_MASK = (1<<7)-1;
uint8_t LLC_MAX_REREF = 127;

int my_llc_ceil(int x, int y) {
  return (x + y - 1) / y;
}

uint64_t next_access(NodeID idx, Graph* G, NodeID currDst, vector<uint8_t> &rerefMatrix){
    int vertices_per_epoch = my_llc_ceil(G -> num_nodes(), LLC_NUM_EPOCHS);
    int vertices_per_sub_epoch = my_llc_ceil(vertices_per_epoch,LLC_NUM_EPOCHS/2);
    int vertices_per_line = BLOCK_SIZE / (int)sizeof(int);
    int epoch = currDst / vertices_per_epoch; 
    int cache_line_no = idx / vertices_per_line;
    int numCacheLines = my_llc_ceil(G -> num_nodes(), vertices_per_line);
    if((rerefMatrix[epoch*numCacheLines+cache_line_no]&LLC_MSB_MASK)>0){
        return rerefMatrix[epoch*numCacheLines+cache_line_no] & LLC_NO_MSB_MASK;
    } else {
        int sub_epoch_pos = currDst - epoch * numCacheLines;
        int sub_epoch_number = sub_epoch_pos / vertices_per_sub_epoch;
        if(rerefMatrix[epoch*numCacheLines+cache_line_no]>=sub_epoch_number){
            return 0;
        } else {
            if((rerefMatrix[(epoch+1)*numCacheLines+cache_line_no]&LLC_MSB_MASK)>0){
                if(rerefMatrix[(epoch+1)*numCacheLines+cache_line_no]==LLC_MAX_REREF) {
                    return LLC_MAX_REREF;
                } else {
                    return rerefMatrix[(epoch+1)*numCacheLines+cache_line_no]+1;
                }
            }
            else {
                return 1;
            }
        }
    }
}


// BLOCK - NOde N 
// CURRDST = Di
// NODE N - in_neighs - upper_bound([N1,N2,...Nk],Di) - Nj
// Across all N - pick N with Nj maximum

// find replacement victim
uint32_t CACHE::llc_find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set,
                                const BLOCK *current_set, uint64_t ip,
                                uint64_t full_addr, uint32_t type) {
  // look for the maxRRPV line
  if((uncore.LLC.irreg_data_base<0) || (uncore.LLC.curr_dst_vertex<0)){
    while (1) {
        for (int i = 0; i < LLC_WAY; i++)
        if (rrpv[set][i] == maxRRPV)
            return i;

        for (int i = 0; i < LLC_WAY; i++)
        rrpv[set][i]++;
    }

    // WE SHOULD NOT REACH HERE
    assert(0);
    return 0;
  } else {
    uint64_t vfull_addr = popt_pa_to_va(full_addr); // Inverse check of virtual address as base and bound are virtual

    uint64_t next_reference, max_next_reference = 0;
    uint64_t best_way = LLC_WAY;

    if ((uncore.LLC.irreg_data_base<=vfull_addr) && (vfull_addr<uncore.LLC.irreg_data_bound)) {
        next_reference = ULLONG_MAX;
        NodeID curr_idx = (vfull_addr - uncore.LLC.irreg_data_base) / sizeof(int);
        next_reference = next_access(curr_idx,&uncore.LLC.matrix,uncore.LLC.curr_dst_vertex,uncore.LLC.rerefMatrix);
        max_next_reference = next_reference;

        uint64_t numVertices = BLOCK_SIZE / (sizeof(int));    

        for(int way=0;way<LLC_WAY;way++){
            next_reference = ULLONG_MAX;
            if(!current_set[way].valid || !current_set[way].used){
                return way;
            }
        }
        for(int way=0;way<LLC_WAY;way++){
            uint64_t block_va = popt_pa_to_va(current_set[way].address << LOG2_BLOCK_SIZE);
            if( (block_va < uncore.LLC.irreg_data_base) || (block_va >= uncore.LLC.irreg_data_bound)){
                return way;
            }
        }
        for(int way=0;way<LLC_WAY;way++){
        uint64_t block_va = popt_pa_to_va(current_set[way].address << LOG2_BLOCK_SIZE);
	    uint64_t block_idx = (block_va - uncore.LLC.irreg_data_base) / sizeof(int);
            for(uint64_t vertex=0;vertex<numVertices;vertex++){
                uint64_t word_idx = block_idx+vertex;
                uint64_t temp_reference;
                if (word_idx < uncore.LLC.matrix.num_nodes()){
                    temp_reference = next_access(word_idx,&uncore.LLC.matrix,uncore.LLC.curr_dst_vertex,uncore.LLC.rerefMatrix);
                    next_reference = min(next_reference,temp_reference);
                }
            }
            if(next_reference == ULLONG_MAX){
                return way;
            }
            if(next_reference>max_next_reference){
                max_next_reference = next_reference;
                best_way = way;
            }
        }
        if((best_way == LLC_WAY) && (type==WRITEBACK)){
            while (1) {
                for (int i = 0; i < LLC_WAY; i++)
                if (rrpv[set][i] == maxRRPV)
                    return i;

                for (int i = 0; i < LLC_WAY; i++)
                rrpv[set][i]++;
            }
            assert(0);
        }
        return best_way;
    }
    while (1) {
        for (int i = 0; i < LLC_WAY; i++)
        if (rrpv[set][i] == maxRRPV)
            return i;

        for (int i = 0; i < LLC_WAY; i++)
        rrpv[set][i]++;
    }
    assert(0);
    return LLC_WAY;
  }
}



// use this function to print out your own stats at the end of simulation
void CACHE::llc_replacement_final_stats() {
    cout<<"Total LLC accesses: "<<num_future_accesses<<endl; // 20000
    cout<<"Total Irreg accesses: "<<num_accesses<<endl; // 410
}
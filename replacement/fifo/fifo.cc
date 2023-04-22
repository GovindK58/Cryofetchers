#include "cache.h"

// initialize replacement state
void CACHE::initialize_replacement()
{

}

uint32_t CACHE::find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    uint32_t way = 0;

    // fill invalid line first
    for (way=0; way<NUM_WAY; way++) {
        if (block[set][way].valid == false) {

            DP ( if (warmup_complete[cpu]) {
            cout << "[" << NAME << "] " << __func__ << " instr_id: " << instr_id << " invalid set: " << set << " way: " << way;
            cout << hex << " address: " << (full_addr>>LOG2_BLOCK_SIZE) << " victim address: " << block[set][way].address << " data: " << block[set][way].data;
            cout << dec << " lru: " << block[set][way].lru << endl; });

            return way;
        }
    }
    
    // choosing max way
    int tmp = block[set][0].lru, max_way = 0;
    for (way = 1; way < NUM_WAY; way ++){
        if (block[set][way].lru > tmp){
            tmp = block[set][way].lru;
            max_way = way;
        }
    }
    way = max_way;

    DP ( if (warmup_complete[cpu]) {
        cout << "[" << NAME << "] " << __func__ << " instr_id: " << instr_id << " invalid set: " << set << " way: " << way;
        cout << hex << " address: " << (full_addr>>LOG2_BLOCK_SIZE) << " victim address: " << block[set][way].address << " data: " << block[set][way].data;
        cout << dec << " lru: " << block[set][way].lru << endl; });

    return way;

}

void CACHE::update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{
    string TYPE_NAME;
    if (type == LOAD)
        TYPE_NAME = "LOAD";
    else if (type == RFO)
        TYPE_NAME = "RFO";
    else if (type == PREFETCH)
        TYPE_NAME = "PF";
    else if (type == WRITEBACK)
        TYPE_NAME = "WB";
    else
        assert(0);

    if (hit)
        TYPE_NAME += "_HIT";
    else
        TYPE_NAME += "_MISS";

    if ((type == WRITEBACK) && ip)
        assert(0);


    if (! hit) 
        // if miss move everything ahead
        for (uint32_t i=0; i<NUM_WAY; i++) {
            block[set][i].lru++;
        }
        // and bring this line to the first position
        block[set][way].lru = 0; 

        // if hit, mothing is entered so nothing's done
}

void CACHE::replacement_final_stats()
{

}
#include "cache.h"

// initialize replacement state
void CACHE::initialize_replacement()
{

}

uint32_t CACHE::find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    // uint32_t way = 0;
    
    // choosing max way

    return std::distance(current_set, std::max_element(current_set, std::next(current_set, NUM_WAY), lru_comparator<BLOCK, BLOCK>()));


    // int tmp = block[set*NUM_WAY + 0].lru, max_way = 0;
    // for (way = 1; way < NUM_WAY; way ++){
    //     if (block[set][way].lru > tmp){
    //         tmp = block[set][way].lru;
    //         max_way = way;
    //     }
    // }
    // way = max_way;

    // return way;

}

void CACHE::update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{

    if ((type == WRITEBACK) && ip)
        assert(0);

    if (! hit) 
        // if miss move everything ahead
            
        for (uint32_t i=0; i<NUM_WAY; i++) {
            block[set*NUM_WAY + i].lru++;
        }
        // and bring this line to the first position
        block[set*NUM_WAY + way].lru = 0; 

        // if hit, mothing is entered so nothing's done
}

void CACHE::replacement_final_stats()
{

}
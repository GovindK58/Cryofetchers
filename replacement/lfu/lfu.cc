#include "cache.h"

// initialize replacement state
void CACHE::initialize_replacement()
{

}

uint32_t CACHE::find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{

    return std::distance(current_set, std::min_element(current_set, std::next(current_set, NUM_WAY), lru_comparator<BLOCK, BLOCK>()));

}

void CACHE::update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{
    if ((type == WRITEBACK) && ip)
        assert(0);

    auto begin = std::next(block.begin(), set * NUM_WAY);
    if (! hit){ 
        // if miss promote to the least position
        std::next(begin, way)->lru = 0; 
    }
    else {
        // increase the frequency of the hit line
        std::next(begin, way)->lru ++; 
    }
}

void CACHE::replacement_final_stats()
{

}
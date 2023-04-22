#include "cache.h"

// initialize replacement state
void CACHE::initialize_replacement()
{

}

uint32_t CACHE::find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{

  return std::distance(current_set, std::max_element(current_set, std::next(current_set, NUM_WAY), lru_comparator<BLOCK, BLOCK>()));


}

void CACHE::update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{

    if ((type == WRITEBACK) && ip)
        assert(0);


    auto begin = std::next(block.begin(), set * NUM_WAY);
    auto end = std::next(begin, NUM_WAY);

    if (! hit){
        // update lru replacement state
        uint32_t tmp = rand() % min(NUM_WAY, (uint32_t)4);

        // for (uint32_t i=0; i<NUM_WAY; i++){
        //     if (block[set][i].lru >= tmp) {
        //         block[set][i].lru++;
        //     }
        // }
        // block[set][way].lru = tmp; // promote to the tmp position

        std::for_each(begin, end, [tmp](BLOCK& x) {
            if (x.lru >= tmp)
            x.lru++;
        });

        std::next(begin, way)->lru = tmp;

    }
    else {


        if (std::next(begin, way)->lru >= NUM_WAY/2){
            uint32_t tmp = rand() % min(NUM_WAY, (uint32_t)4);

            // for (uint32_t i=0; i<NUM_WAY; i++){
            //     if (block[set][i].lru < block[set][way].lru && block[set][i].lru >= tmp) {
            //         block[set][i].lru++;
            //     }
            // }
            // block[set][way].lru = tmp;

            uint32_t hit_lru = std::next(begin, way)->lru;

            std::for_each(begin, end, [tmp, hit_lru](BLOCK& x) {
                if (x.lru >= tmp && x.lru < hit_lru)
                x.lru++;
            });

            std::next(begin, way)->lru = tmp;
        }
    }
}

void CACHE::replacement_final_stats()
{

}

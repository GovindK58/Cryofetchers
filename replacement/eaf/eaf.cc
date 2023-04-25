#include "cache.h"

class EAF{
public:
    uint64_t *queue;
    int pos;
    int size;

    EAF(int num){
        queue = new uint64_t[num];
        size = num;
        pos = 0;
    }
    void insert(uint64_t addr){
        queue[pos] = addr;
        pos = (pos + 1) % size;
    }
    bool find(uint64_t addr){
        for (int i = 0; i < size; i++){
            if (queue[i] == addr) return true;
        }
        return false;
    }
    ~EAF(){
        delete[] queue;
    }
};

EAF *cache_eaf;
// initialize replacement state
void CACHE::initialize_replacement()
{
    cache_eaf = new EAF(NUM_SET/2);
}

uint32_t CACHE::find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{

    uint32_t way = std::distance(current_set, std::max_element(current_set, std::next(current_set, NUM_WAY), lru_comparator<BLOCK, BLOCK>()));

    cache_eaf->insert(block[set*NUM_WAY + way].address);

    if (way == NUM_WAY) {
        cerr << "[" << NAME << "] " << __func__ << " no victim! set: " << set << endl;
        assert(0);
    }

    return way;

}

void CACHE::update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit)
{

    if ((type == WRITEBACK) && ip)
        assert(0);


    if (! hit){
        if (cache_eaf->find(block[set*NUM_WAY + way].address)){
            // update lru replacement state
            for (uint32_t i=0; i<NUM_WAY; i++) {
                if (block[set*NUM_WAY + i].lru < block[set*NUM_WAY + way].lru) {
                    block[set*NUM_WAY + i].lru++;
                }
            }
            block[set*NUM_WAY + way].lru = 0; // promote to the MRU position
        }
        else{
            if (rand() % 4 == 0){
                // update lru replacement state
                for (uint32_t i=0; i<NUM_WAY; i++) {
                    if (block[set*NUM_WAY + i].lru < block[set*NUM_WAY + way].lru) {
                        block[set*NUM_WAY + i].lru++;
                    }
                }
                block[set*NUM_WAY + way].lru = 0; // promote to the MRU position
            }
        }
    }
    else {
        // update lru replacement state
        for (uint32_t i=0; i<NUM_WAY; i++) {
            if (block[set*NUM_WAY + i].lru < block[set*NUM_WAY + way].lru) {
                block[set*NUM_WAY + i].lru++;
            }
        }
        block[set*NUM_WAY + way].lru = 0; // promote to the MRU position
    }
}

void CACHE::replacement_final_stats()
{
    delete cache_eaf;
}

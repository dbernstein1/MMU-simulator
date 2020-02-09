page_frame_size = 256
num_pages = 256
num_frames = 256
num_bits_offset = 8
num_entries_TLB = 16
TLB_hits = 0
TLB_FIFO_index = 0
page_faults = 0

TLB = [[None for x in range(2)] for y in range(num_entries_TLB)]
PAGE_TABLE = [None for x in range(num_pages)]
PHYSICAL_STORE = [[None for x in range(page_frame_size)] for y in range(num_frames)]


def main():
    f = open("addresses.txt", 'r')
    for line in f.read().splitlines():
        logical_address = bin(int(line))[2:].zfill(16)
        page_num = int(logical_address[:8], 2)
        offset = int(logical_address[8:], 2)
        print("Reading logical address:", line)
        print("\tPage number:", page_num)
        print("\tOffset:", offset)
        frame = check_tlb(page_num)
        if frame == -1:
            frame = check_page_table(page_num)
            if frame == -1:
                frame = check_open_frame()
                page_fault(page_num, frame)
                update_tables(frame, page_num)
            else:
                print("\tFrame number", frame, "read from page table")
                read_memory(frame, offset)
        else:
            read_memory(frame, offset)
        print("\n")
    print("Aggregate page faults =", page_faults)
    print("Aggregate TLB hits =", TLB_hits)


def dec_to_bin(x):
    return bin(x)[2:]


def update_tables(frame, page):
    global TLB_FIFO_index
    PAGE_TABLE[frame] = page
    print("\tPage table updated at index", page, "with frame number", frame)
    TLB[TLB_FIFO_index][0] = page
    TLB[TLB_FIFO_index][1] = frame
    TLB_FIFO_index = (TLB_FIFO_index + 1) % num_entries_TLB
    print("\tTLB updated with page number", page, "and frame number", frame)


def check_open_frame():
    for i in range(num_pages):
        if PAGE_TABLE[i] is None:
            print("\tFound free frame number:", i)
            return i


def check_page_table(page_num):
    global page_faults
    for i in range(num_pages):
        if PAGE_TABLE[i] == page_num:
            print("\tNo page fault!")
            return i
    page_faults += 1
    print("\tPage fault!")
    return -1


def check_tlb(page_num):
    global TLB_hits
    for i in range(num_entries_TLB):
        if TLB[i][0] == page_num:
            print("\tTLB hit! Frame number:", TLB[i][1])
            TLB_hits += 1
            return TLB[i][1]
    print("\tTLB miss!")
    return -1


def page_fault(page_num, open_frame):
    i = 0
    loc = page_num * page_frame_size
    with open("BACKING_STORE.bin", "rb+") as f:
        f.seek(loc)
        while i < page_frame_size:
            byte = f.read(1)
            PHYSICAL_STORE[open_frame][i] = byte
            i += 1
    print("\tPage loaded from disk to memory")
    return


def read_memory(frame, offset):
    if PHYSICAL_STORE[frame][offset] is not None:
        byte = PHYSICAL_STORE[frame][offset]
        value = int.from_bytes(byte, "little", signed=True)
        print("\tValue in the memory:", value)
    return


main()

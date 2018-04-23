#include "rijndael.c"
#include <stlib.h>
#include "xorshift.c"
#include <stdio.h>
#include <string.h>





int main() {

	char block_contents[] = "agnescam, prela, ampayne";
    do{
        //   Next block's parent, version, difficulty
        next_header = get_next()
        // Construct a block with our name in the contents that appends to the
        // head of the main chain
        cout << "next header is"
        cout << next_header
        new_block = make_block(next_header, block_contents[])
        //Solve the POW
        cout << "Solving block..."
        cout << new_block
        solve_block(new_block)
        //Send to the server
        cout << "Contents:";
        cout << new_block["root"]
        add_block(new_block, block_contents)

    }while(true)

}

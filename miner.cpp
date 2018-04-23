//#include "rijndael.c"
#include <string>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <time.h>
#include <unistd.h>
#include <vector>
#include <sqlite3.h>
#include <iostream> 
#include <math.h>
#include "json.hpp"
#include <fstream>
#include <openssl/sha.h>
#include <curl/curl.h>
using namespace std;
using json = nlohmann::json;


static size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

unsigned char* hash_to_hex(unsigned char* data){
	unsigned char out_buf[20];
	SHA1(data, strlen((char*)data), out_buf);
	int i;
    for (i = 0; i < 20; i++) {
        printf("%02x ", out_buf[i]);
    }
    printf("\n");

    return out_buf;
}

json make_block(json next_info, unsigned char* contents){
	unsigned char* num_in = hash_to_hex(contents);

	json block = {
        {"version", next_info["version"]},
        //for now, root is hash of block contents (team name)
        {"root", 01010},
        {"parentid", next_info["parentid"]},
        //nanoseconds since unix epoch
        //time_t time = time(0); 
        {"timestamp", long(time(0)*1000*1000*1000)},
        {"difficulty", next_info["difficulty"]}
    };
    return block;
}

json get_next(){
  	CURL *curl;
  	CURLcode res;
  	string readBuffer;

	curl = curl_easy_init();

  	if(curl) {
    	curl_easy_setopt(curl, CURLOPT_URL, "http://6857coin.csail.mit.edu/next");
    	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
    	res = curl_easy_perform(curl);
    	curl_easy_cleanup(curl);

    	cout << "read buffer is " << readBuffer << endl;
  	}

  	json buffer = json::parse(readBuffer);

	return buffer;
}

int main() {

	unsigned char* block_contents = (unsigned char*)"agnescam, prela, ampayne";

    do{
        //   Next block's parent, version, difficulty
        json next_header = get_next();
        // Construct a block with our name in the contents that appends to the
        // head of the main chain
        cout << "next header is" << next_header;
        json new_block = make_block(next_header, block_contents);
        // //Solve the POW
        // cout << "Solving block...";
        // cout << new_block;
        // solve_block(new_block);
        // //Send to the server
        // cout << "Contents:";
        // cout << new_block["root"];
        // add_block(new_block, block_contents);

    }while(true);

}

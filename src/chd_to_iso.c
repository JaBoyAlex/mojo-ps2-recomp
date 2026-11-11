/* Bounded single-track CD reader. Decompression is provided by BSD-licensed libchdr. */
#include <libchdr/chd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

int wmain(int argc, wchar_t **argv) {
    if(argc != 3) return 2;
    FILE *input = _wfopen(argv[1], L"rb");
    if(!input) return 20;
    chd_file *chd = NULL;
    if(chd_open_file(input, CHD_OPEN_READ, NULL, &chd) != CHDERR_NONE) { fclose(input); return 20; }
    const chd_header *h = chd_get_header(chd);
    char metadata[512] = {0}, second[512] = {0};
    int track=0, frames=0, pregap=0, postgap=0; char type[64]={0}, sub[64]={0}, pgtype[64]={0}, pgsub[64]={0};
    int good = h->unitbytes == 2448 && h->hunkbytes && h->hunkbytes <= 16*1024*1024 && h->hunkbytes % 2448 == 0;
    chd_error m = chd_get_metadata(chd, CDROM_TRACK_METADATA2_TAG, 0, metadata, sizeof(metadata)-1, NULL, NULL, NULL);
    if(m == CHDERR_NONE) {
        good &= sscanf(metadata, "TRACK:%d TYPE:%63s SUBTYPE:%63s FRAMES:%d PREGAP:%d PGTYPE:%63s PGSUB:%63s POSTGAP:%d", &track,type,sub,&frames,&pregap,pgtype,pgsub,&postgap) == 8;
        good &= chd_get_metadata(chd, CDROM_TRACK_METADATA2_TAG, 1, second, sizeof(second), NULL,NULL,NULL) == CHDERR_METADATA_NOT_FOUND;
    } else {
        good &= chd_get_metadata(chd, CDROM_TRACK_METADATA_TAG, 0, metadata, sizeof(metadata)-1,NULL,NULL,NULL) == CHDERR_NONE;
        good &= sscanf(metadata,"TRACK:%d TYPE:%63s SUBTYPE:%63s FRAMES:%d", &track,type,sub,&frames)==4;
        good &= chd_get_metadata(chd, CDROM_TRACK_METADATA_TAG, 1, second, sizeof(second),NULL,NULL,NULL)==CHDERR_METADATA_NOT_FOUND;
    }
    good &= track==1 && frames>0 && frames<=400000 && pregap==0 && postgap==0;
    good &= (uint64_t)frames*2448 <= h->logicalbytes;
    unsigned offset = 0;
    if(!strcmp(type,"MODE2_RAW")) offset=24;
    else if(!strcmp(type,"MODE1_RAW")) offset=16;
    else if(strcmp(type,"MODE1") && strcmp(type,"MODE2_FORM1")) good=0;
    if(!good) { chd_close(chd); fclose(input); return 20; }
    FILE *out=_wfopen(argv[2],L"wb");
    unsigned char *buffer=malloc(h->hunkbytes);
    if(!out || !buffer) { if(out) fclose(out); free(buffer); chd_close(chd); fclose(input); return 21; }
    unsigned current=~0u; int result=0;
    for(int frame=0; frame<frames; ++frame) {
        uint64_t pos=(uint64_t)frame*2448; unsigned hunk=(unsigned)(pos/h->hunkbytes);
        if(current!=hunk) {
            if(chd_read(chd,hunk,buffer)!=CHDERR_NONE) { result=20; break; }
            current=hunk;
        }
        if(fwrite(buffer+(pos%h->hunkbytes)+offset,1,2048,out)!=2048) { result=21; break; }
    }
    if(fclose(out)) result=21;
    free(buffer); chd_close(chd); fclose(input);
    return result;
}

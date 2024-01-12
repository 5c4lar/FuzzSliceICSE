/* TEMPLATE GENERATED TESTCASE FILE
Filename: CWE122_Heap_Based_Buffer_Overflow__c_dest_char_cpy_82_goodG2B.cpp
Label Definition File: CWE122_Heap_Based_Buffer_Overflow__c_dest.label.xml
Template File: sources-sink-82_goodG2B.tmpl.cpp
*/
/*
 * @description
 * CWE: 122 Heap Based Buffer Overflow
 * BadSource:  Allocate using malloc() and set data pointer to a small buffer
 * GoodSource: Allocate using malloc() and set data pointer to a large buffer
 * Sinks: cpy
 *    BadSink : Copy string to data using strcpy
 * Flow Variant: 82 Data flow: data passed in a parameter to an virtual method called via a pointer
 *
 * */
#ifndef OMITGOOD

#include "std_testcase.h"
#include "CWE122_Heap_Based_Buffer_Overflow__c_dest_char_cpy_82.h"

namespace CWE122_Heap_Based_Buffer_Overflow__c_dest_char_cpy_82
{

void CWE122_Heap_Based_Buffer_Overflow__c_dest_char_cpy_82_goodG2B::action(char * data)
{
    {
        char source[100];
        memset(source, 'C', 100-1); /* fill with 'C's */
        source[100-1] = '\0'; /* null terminate */
        /* POTENTIAL FLAW: Possible buffer overflow if source is larger than data */
        strcpy(data, source);
        printLine(data);
        free(data);
    }
}

}
#endif /* OMITGOOD */

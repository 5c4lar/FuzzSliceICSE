/* TEMPLATE GENERATED TESTCASE FILE
Filename: CWE122_Heap_Based_Buffer_Overflow__cpp_CWE129_connect_socket_51a.cpp
Label Definition File: CWE122_Heap_Based_Buffer_Overflow__cpp_CWE129.label.xml
Template File: sources-sinks-51a.tmpl.cpp
*/
/*
 * @description
 * CWE: 122 Heap Based Buffer Overflow
 * BadSource: connect_socket Read data using a connect socket (client side)
 * GoodSource: Larger than zero but less than 10
 * Sinks:
 *    GoodSink: Ensure the array index is valid
 *    BadSink : Improperly check the array index by not checking the upper bound
 * Flow Variant: 51 Data flow: data passed as an argument from one function to another in different source files
 *
 * */

#include "std_testcase.h"

#ifdef _WIN32
#include <winsock2.h>
#include <windows.h>
#include <direct.h>
#pragma comment(lib, "ws2_32") /* include ws2_32.lib when linking */
#define CLOSE_SOCKET closesocket
#else /* NOT _WIN32 */
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#define INVALID_SOCKET -1
#define SOCKET_ERROR -1
#define CLOSE_SOCKET close
#define SOCKET int
#endif

#define TCP_PORT 27015
#define IP_ADDRESS "127.0.0.1"
#define CHAR_ARRAY_SIZE (3 * sizeof(data) + 2)

namespace CWE122_Heap_Based_Buffer_Overflow__cpp_CWE129_connect_socket_51
{

#ifndef OMITBAD

/* bad function declaration */
void badSink(int data);

void bad()
{
    int data;
    /* Initialize data */
    data = -1;
    {
#ifdef _WIN32
        WSADATA wsaData;
        int wsaDataInit = 0;
#endif
        int recvResult;
        struct sockaddr_in service;
        SOCKET connectSocket = INVALID_SOCKET;
        char inputBuffer[CHAR_ARRAY_SIZE];
        do
        {
#ifdef _WIN32
            if (WSAStartup(MAKEWORD(2,2), &wsaData) != NO_ERROR)
            {
                break;
            }
            wsaDataInit = 1;
#endif
            /* POTENTIAL FLAW: Read data using a connect socket */
            connectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
            if (connectSocket == INVALID_SOCKET)
            {
                break;
            }
            memset(&service, 0, sizeof(service));
            service.sin_family = AF_INET;
            service.sin_addr.s_addr = inet_addr(IP_ADDRESS);
            service.sin_port = htons(TCP_PORT);
            if (connect(connectSocket, (struct sockaddr*)&service, sizeof(service)) == SOCKET_ERROR)
            {
                break;
            }
            /* Abort on error or the connection was closed, make sure to recv one
             * less char than is in the recv_buf in order to append a terminator */
            recvResult = recv(connectSocket, inputBuffer, CHAR_ARRAY_SIZE - 1, 0);
            if (recvResult == SOCKET_ERROR || recvResult == 0)
            {
                break;
            }
            /* NUL-terminate the string */
            inputBuffer[recvResult] = '\0';
            /* Convert to int */
            data = atoi(inputBuffer);
        }
        while (0);
        if (connectSocket != INVALID_SOCKET)
        {
            CLOSE_SOCKET(connectSocket);
        }
#ifdef _WIN32
        if (wsaDataInit)
        {
            WSACleanup();
        }
#endif
    }
    badSink(data);
}

#endif /* OMITBAD */

#ifndef OMITGOOD

/* good function declarations */
void goodG2BSink(int data);
void goodB2GSink(int data);

/* goodG2B uses the GoodSource with the BadSink */
static void goodG2B()
{
    int data;
    /* Initialize data */
    data = -1;
    /* FIX: Use a value greater than 0, but less than 10 to avoid attempting to
     * access an index of the array in the sink that is out-of-bounds */
    data = 7;
    goodG2BSink(data);
}

/* goodB2G uses the BadSource with the GoodSink */
static void goodB2G()
{
    int data;
    /* Initialize data */
    data = -1;
    {
#ifdef _WIN32
        WSADATA wsaData;
        int wsaDataInit = 0;
#endif
        int recvResult;
        struct sockaddr_in service;
        SOCKET connectSocket = INVALID_SOCKET;
        char inputBuffer[CHAR_ARRAY_SIZE];
        do
        {
#ifdef _WIN32
            if (WSAStartup(MAKEWORD(2,2), &wsaData) != NO_ERROR)
            {
                break;
            }
            wsaDataInit = 1;
#endif
            /* POTENTIAL FLAW: Read data using a connect socket */
            connectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
            if (connectSocket == INVALID_SOCKET)
            {
                break;
            }
            memset(&service, 0, sizeof(service));
            service.sin_family = AF_INET;
            service.sin_addr.s_addr = inet_addr(IP_ADDRESS);
            service.sin_port = htons(TCP_PORT);
            if (connect(connectSocket, (struct sockaddr*)&service, sizeof(service)) == SOCKET_ERROR)
            {
                break;
            }
            /* Abort on error or the connection was closed, make sure to recv one
             * less char than is in the recv_buf in order to append a terminator */
            recvResult = recv(connectSocket, inputBuffer, CHAR_ARRAY_SIZE - 1, 0);
            if (recvResult == SOCKET_ERROR || recvResult == 0)
            {
                break;
            }
            /* NUL-terminate the string */
            inputBuffer[recvResult] = '\0';
            /* Convert to int */
            data = atoi(inputBuffer);
        }
        while (0);
        if (connectSocket != INVALID_SOCKET)
        {
            CLOSE_SOCKET(connectSocket);
        }
#ifdef _WIN32
        if (wsaDataInit)
        {
            WSACleanup();
        }
#endif
    }
    goodB2GSink(data);
}

void good()
{
    goodG2B();
    goodB2G();
}

#endif /* OMITGOOD */

} /* close namespace */

/* Below is the main(). It is only used when building this testcase on
   its own for testing or for building a binary to use in testing binary
   analysis tools. It is not used when compiling all the testcases as one
   application, which is how source code analysis tools are tested. */

#ifdef INCLUDEMAIN

using namespace CWE122_Heap_Based_Buffer_Overflow__cpp_CWE129_connect_socket_51; /* so that we can use good and bad easily */

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );
#ifndef OMITGOOD
    printLine("Calling good()...");
    good();
    printLine("Finished good()");
#endif /* OMITGOOD */
#ifndef OMITBAD
    printLine("Calling bad()...");
    bad();
    printLine("Finished bad()");
#endif /* OMITBAD */
    return 0;
}

#endif

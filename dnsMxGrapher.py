import dns.resolver
import networkx as nx
import sys

def main():
    
    domainFilename = 'NA'
    
    isWriteGraphml = False
    graphmlOutputFilename = 'NA'
    
    isWriteCsv = False
    csvOutputFilename = 'NA'
    
    #At minimum we need a domain file as input
    if '-domains' in sys.argv:
        domainFilename = sys.argv[sys.argv.index('-domains') + 1]
    else:
        printUsage()
        sys.exit('Need domain list filename. Ex: ' + sys.argv[0] + ' domains.txt');
    
    #Check if graphml output is desired
    if '-graphml' in sys.argv:
        isWriteGraphml = True
        graphmlOutputFilename = sys.argv[sys.argv.index('-graphml') + 1]
    
    #Check if csv output is desired
    if '-csv' in sys.argv:
        isWriteCsv = True
        csvOutputFilename = sys.argv[sys.argv.index('-csv') + 1]
    
    print('Getting MX data: Started')
    domainToMxSetMap = getMxMapping(domainFilename)
    print('Getting MX data: Done')
    
    if isWriteGraphml:
        print('Writing graphml file')
        diGraph = getDirectedGraph(domainToMxSetMap)
        convertToGraphmlLines(diGraph, graphmlOutputFilename)
    
    if isWriteCsv:
        print('Writing csv file')
        csvLines = convertToCsvLines(domainToMxSetMap)
        writeLinesToFile(csvOutputFilename, csvLines)
    
def printUsage():
    print(sys.argv[0] + ' Usage')
    print("\tRead MX domains and print          |  " + sys.argv[0] + ' -domains filename')
    print("\tWrite output as graphml            |  " + sys.argv[0] + ' -domains filename -graphml outputFilename')
    print("\tWrite output as csv                |  " + sys.argv[0] + ' -domains filename -csv outputFilename')
    print("\tWrite output as graphml and csv    |  " + sys.argv[0] + ' -domains filename -graphml outputFilename -csv outputFilename')
    print()
    
    
def writeLinesToFile(filename, lines):
    outputFile = open(filename,'w')
    
    for line in lines:
        outputFile.write(line + '\n')
        
    outputFile.close()
    
def convertToGraphmlLines(directedGraph, graphmlFilename):
    nx.write_graphml(directedGraph, graphmlFilename)
    
def convertToCsvLines(domainToMxSetMap):
  
    lines = []
    
    lines.append('domain,mxDomain')
    
    for domain,mxSet in domainToMxSetMap.items():
    
        for mxDomain in mxSet:
            lines.append(domain + ',' + mxDomain)
  
    return lines

def getDirectedGraph(domainToMxSetMap):

    DG=nx.DiGraph()
    
    #Add nodes
    domainSet = set()
    domainKeys = sorted(domainToMxSetMap.keys())
    domainSet.update(domainKeys)
        
    #MX domain nodes
    for domain,mxSet in domainToMxSetMap.items():
        domainSet.update(mxSet)
    
    for domain in domainSet:
        nodeType = 'domain' if domain in domainKeys else 'mxDomain'
        DG.add_node(domain, type=nodeType, label=domain)
    
    #Add edges
    for domain,mxSet in domainToMxSetMap.items():
        for mxDomain in mxSet:
            DG.add_edge(domain,mxDomain)
            
    return DG
    
def getMxMapping(domainsFilename):

    domainToMxSetMap = {}
    
    #Open file containing domain names
    with open(domainsFilename) as f:
        
        for domain in f:
      
            #Remove any whitespace from the raw line
            domain = domain.strip()
    
            print('Querying for MX record for domain: ' + domain)
    
            #Use a set to derive unique entries without reinventing the wheel
            mxRecordSet = set()
            
            #Query for DNS MX records. Loop over each Name object. 
            try:
                for mxData in dns.resolver.query(domain, 'MX'):
                    
                    #Only split and use records that look like a domain name
                    if '.' in mxData.exchange.to_text(True):
                                    
                        #Split into TLD and name. Goal here is to remove specific subdomains
                        splitMxExchange = mxData.exchange.split(3)
                        
                        #Some domains are all uppercase. Some lower. Let's make 
                        #them the same here
                        mxDomain = splitMxExchange[1].to_text(True).lower()
                        
                        #Add to the set. Will write to the file later after using the set
                        #to derive only unique entries
                        mxRecordSet.add(mxDomain)
                    else:
                        print('Could not determine if this was a valid domain name. Found: ' + mxData.exchange.to_text(True));
                    
                domainToMxSetMap[domain] = mxRecordSet;
            except KeyError:
                print('Could not get MX record for: ' + domain + '. Received: KeyError');
            except dns.resolver.NoAnswer:
                print('Could not get MX record for: ' + domain + '. Received: NoAnswer');
                
    return domainToMxSetMap

if __name__== "__main__":
    main()            
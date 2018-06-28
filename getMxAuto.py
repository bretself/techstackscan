import dns.resolver

def main():
    domainToMxSetMap = getMxAndWriteFile('domains.txt')
    graphmlLines = convertToGraphmlLines(domainToMxSetMap)
    
    writeLinesToFile('domainMx.graphml', graphmlLines)
    
    #gmlLines = convertToGmlLines(domainToMxSetMap)
    #writeLinesToFile('domainMx.gml', gmlLines)
    
def writeLinesToFile(filename, lines):
    outputFile = open(filename,'w')
    
    for line in lines:
        outputFile.write(line + '\n')
        
    outputFile.close()

def convertToGmlLines(domainToMxSetMap):
    #graph [
    #        comment "This is a sample graph"
    #        directed 1
    #        id n42
    #        label "Hello, I am a graph"
    #        node [
    #                id 1
    #                label "node 1"
    #                thisIsASampleAttribute 42
    #        ]
    #        node [
    #                id 2
    #                label "node 2"
    #                thisIsASampleAttribute 43
    #        ]
    #        node [
    #                id 3
    #                label "node 3"
    #                thisIsASampleAttribute 44
    #        ]
    #        edge [
    #                source 1
    #                target 2
    #                label "Edge from node 1 to node 2"
    #        ]
    #        edge [
    #                source 2
    #                target 3
    #                label "Edge from node 2 to node 3"
    #        ]
    #        edge [
    #                source 3
    #                target 1
    #                label "Edge from node 3 to node 1"
    #        ]
    #]
    
    lines = []
    
    #Start new graph
    lines.append('graph [')
    lines.append('\tdirected 1')
    lines.append('\tid 001')
    lines.append('\tlabel "MX Graph"')
    
    #Create nodes
    #        node [
    #                id 1
    #                label "node 1"
    #                thisIsASampleAttribute 42
    #        ]
    
    domainSet = set()
    domainSet.update(sorted(domainToMxSetMap.keys()))
        
    #MX domain nodes
    for domain,mxSet in domainToMxSetMap.items():
        domainSet.update(mxSet)
    
    for domain in domainSet:
        lines.append('\tnode [')
        lines.append('\t\tid "'+domain.replace('.','')+'"')
        lines.append('\t\tlabel "'+domain+'"')
        lines.append('\t]')
    
    #Create edges
    #        edge [
    #                source 3
    #                target 1
    #                label "Edge from node 3 to node 1"
    #        ]
    for domain,mxSet in domainToMxSetMap.items():
    
        idIndex = 0
        for mxDomain in mxSet:
            lines.append('\tedge [')
            lines.append('\t\tsource "'+domain.replace('.','')+'"')
            lines.append('\t\ttarget "'+mxDomain.replace('.','')+'"')
            lines.append('\t]')
            idIndex += 1
    
    #End graph
    lines.append(']')
    
    return lines
    
def convertToGraphmlLines(domainToMxSetMap):
    
    lines = []

    #<?xml version="1.0" encoding="UTF-8"?>
    #<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
    #    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    #    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    #  <graph id="G" edgedefault="undirected">
    #    <node id="n0"/>
    #    <node id="n1"/>
    #    <edge id="e1" source="n0" target="n1"/>
    #  </graph>
    #</graphml>
    
    #print graphml header
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"')
    lines.append('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
    lines.append('    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">')
    
    #Add shape definitions
    lines.append('<key id="shape" for="node" attr.name="shape" attr.type="string"/>')
    
    #Start new graph
    lines.append('  <graph id="G" edgedefault="directed">')
    
    #Create nodes
    
    domainSet = set()
    domainKeys = sorted(domainToMxSetMap.keys())
    domainSet.update(domainKeys)
        
    #MX domain nodes
    for domain,mxSet in domainToMxSetMap.items():
        domainSet.update(mxSet)
    
    for domain in domainSet:
        lines.append('\t<node id="'+domain+'">')
        
        shape = 'RECTANGLE'
        if domain in domainKeys:
            shape = 'ELLIPSE'
        
        lines.append('\t\t<data key="shape">'+shape+'</data>')
        lines.append('\t</node>')
    
    #Create edges
    for domain,mxSet in domainToMxSetMap.items():
    
        idIndex = 0
        for mxDomain in mxSet:
            lines.append('\t<edge id="'+ domain + str(idIndex)+'" source="'+domain+'" target="'+mxDomain+'" />')
            idIndex += 1
    
    #End graph
    lines.append('  </graph>')
    
    #End graphml file
    lines.append('</graphml>')
    
    return lines
    
    
def getMxAndWriteFile(domainsFilename):
    #Open output file for writing
    outputFile = open('domainMx.csv','w')

    #Write CSV header line
    header = 'domain,mx'
    print(header)
    outputFile.write(header + '\n')

    domainToMxSetMap = {}
    
    #Open file containing domain names
    with open(domainsFilename) as f:
        
        for domain in f:
      
            #Remove any whitespace from the raw line
            domain = domain.strip()
            
            #Use a set to derive unique entries without reinventing the wheel
            mxRecordSet = set()
            
            #Query for DNS MX records. Loop over each Name object. 
            for mxData in dns.resolver.query(domain, 'MX'):
                
                #Split into TLD and name. Goal here is to remove specific subdomains
                splitMxExchange = mxData.exchange.split(3)
                
                #Some domains are all uppercase. Some lower. Let's make 
                #them the same here
                mxDomain = splitMxExchange[1].to_text(True).lower()
                
                #Add to the set. Will write to the file later after using the set
                #to derive only unique entries
                mxRecordSet.add(mxDomain)
                
            domainToMxSetMap[domain] = mxRecordSet
                
            #Write the unique entries    
            for mx in mxRecordSet:
                mxLine = domain + ',' + mx
                print(mxLine)
                outputFile.write(mxLine + '\n')
                
    return domainToMxSetMap

    outputFile.close()

if __name__== "__main__":
    main()            
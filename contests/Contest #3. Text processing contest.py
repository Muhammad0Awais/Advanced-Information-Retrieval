import requests

dictionary = requests.get('https://raw.githubusercontent.com/IUCVLab/information-retrieval/main/datasets/small-dict.txt').text.split()

def fix_typo(data, dictionary = dictionary):
    def edit_dist(s1, s2) -> int:
        # TODO compute the Damerau-Levenshtein distance between two given strings (s1 and s2)
            def dp(i, j):
                #base case
                if i == -1:
                    return j + 1
                elif j == -1:
                    return i + 1
                elif s1[i] == s2[j]:
                    return dp(i - 1, j - 1)
                else:
                    return min(
                        dp(i, j - 1) + 1, 
                        dp(i - 1, j) + 1, 
                        dp(i - 1, j - 1) + 1
                        )

            return dp(len(s1) - 1, len(s2) - 1)
    res=[]
    val = ""
    if len(data)<=6:      
      for word in dictionary:
          res.append((word,edit_dist(data, word)))
      min_dist=min(res,key=lambda x:x[1])[1]
      
      result=[]
      for r in res:
          if r[1]==min_dist:
              result.append(r[0])
      val = result[0]
    else:
      val = typoCorrector(data)
    return val

def typoCorrector(typo):  
  scores = []

  for i in dictionary:
    score = 0
    if len(i) <= len(typo):
      for j in range(len(i)):
        # if j != 0 and j< len(typo):
        if typo[j].lower() == i[j].lower():
          score +=1
    else:
      for j in range(len(typo)):
        if typo[j].lower() == i[j].lower():
          score +=1
    scores.append(score)
  
  closeIndex = scores.index(max(scores))
  
  return dictionary[closeIndex]

def wildCardEnteries(s, p):  
    dp = [set() for _ in range(len(p)+1)]

    dp[0].add(-1)
    
    for i in range(len(p)):
        if p[i] == '*':
            minx = len(s)
            for x in dp[i]: minx = min(minx, x)
            while minx < len(s):
                dp[i+1].add(minx)
                minx += 1
        
        else:
            for x in dp[i]:
                if x+1 < len(s) and s[x+1] == p[i]:
                    dp[i+1].add(x+1)
    
    if len(s)-1 in dp[-1]:
        return True
    
    return False

def getwildCards(data):
  output = []
  for word in dictionary:
    val = wildCardEnteries(word, data)
    if val:
      output.append(word)
  return sorted(output)

with open('input.txt', 'r') as f:
    action = f.readline().strip()
    data = f.readline().strip()
    if 'typo' == action:
        outputText = [fix_typo(data)]
        # outputText = [str(data)]
        pass
    elif 'wildcard' == action:
        outputText = getwildCards(data)
        # outputText = [str(data), str(data)]
        pass

with open('output.txt', 'w') as f:
  f.write("\n".join(outputText))

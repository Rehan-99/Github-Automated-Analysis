import streamlit as st
from github import Github,GithubException
import openai
import requests

# Set up the OpenAI API credentials
openai.api_key = 'YOUR-OPEN-API-KEY'

# Constants
MAX_TOKENS = 1000  # Maximum tokens for GPT completion


# Extract the username from the GitHub user URL
global username


#Analyze code complexity using LangChain
def analyze_code_complexity(prompt):
    # Make a request to LangChain for code complexity analysis
    # Replace 'YOUR_LANGCHAIN_API_KEY' with your actual LangChain API key

    response = openai.Completion.create(
        engine='text-davinci-002',  # Specify the LangChain model
        prompt=prompt,
        max_tokens=MAX_TOKENS,  # Set the desired length of the generated completion
        n=1,  # Number of completions to generate
        stop=None,  # Specify any stopping criteria if needed
    )

    # Process the response to retrieve the complexity score
    model_resp = response.choices[0].text.strip()

    return model_resp


def analyze_github_repository(user_url):
    # Create a PyGitHub instance using your personal access token
    g = Github('YOUR-GITHUB-API-KEY')

    # Extract the username from the GitHub user URL
    username = user_url.split('/')[-1]
    print("analysing github repo....")

    def fetch_repo():
        
        try:
            # Get the user object from the username
            # Make a GET request to the GitHub API to fetch the user's repositories
            response = requests.get(f"https://api.github.com/users/{username}/repos")

            if response.status_code == 200:
                # Parse the JSON response
                repositories = response.json()
                print("fetching completed")
                return repositories
    
            
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to fetch repositories - {e}")
            return None

        
    def fork_status(repo):
        try:  
            response = requests.get(f"https://api.github.com/repos/{username}/{repo}")
            if response.status_code == 200:
                
                stats = response.json()
                is_forked = stats['fork']
                print("fork completed")
                return is_forked
            else:
                print(f"Error: Failed to fork status  (Status code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to check fork status - {e}")
            return None

        return None

    def fork_count(repo):
        try:
            response = requests.get(f"https://api.github.com/repos/{username}/{repo}")
            if response.status_code == 200:
                
                stats = response.json()

                fork = stats['forks_count']
                print("fork count completed")
                return fork
            else:
                print(f"Error: Failed to fork counts (Status code: {response.status_code})")
        except Exception as e:
            print(f"Error: {e}")

        return None



    def total_commits(repo):
        try:
            response = requests.get(f"https://api.github.com/repos/{username}/{repo}/commits")
            if response.status_code == 200:
                commit = response.json()
                total_commit = len(commit)
                print("commit completed")
                return total_commit
            else:
                print(f"Error: Failed to fetch commits (Status code: {response.status_code})")
        except Exception as e:
            print(f"Error: {e}")

        return None


    def contributers(repo):
        try:
            response = requests.get(f"https://api.github.com/repos/{username}/{repo}/contributors")
            if response.status_code == 200:
                contro = response.json()
                contributors = [c for c in contro]
                print("contibuters  completed")
                return contributors

        except Exception as e:
            print(f"Error: {e}")
        


    
        
    def get_repository_issues(username, repo):

        # Make a request to the GitHub API to fetch the repository information
        response = requests.get(f"https://api.github.com/repos/{username}/{repo}")
        if response.status_code == 200:
            repo_data = response.json()
            # Extract the issue count information
            open_issues_count = repo_data['open_issues_count']
            
            # Make a request to the GitHub API to fetch the list of issues
            issues_response = requests.get(f"https://api.github.com/repos/{username}/{repo}/issues?state=all")
            if issues_response.status_code == 200:
                issues_data = issues_response.json()
                resolved_issues_count = 0
                unresolved_issues_count = 0
                
                # Calculate the count of resolved and unresolved issues
                for issue in issues_data:
                    if issue['state'] == 'open':
                        unresolved_issues_count += 1
                    else:
                        resolved_issues_count += 1
                print("fetching issues completed")
                
                return resolved_issues_count, unresolved_issues_count
            
        return 0, 0


    try:
        repo_names=[]
       
        rep=fetch_repo()
        print(rep[0])
        for repo in rep:
            repo_name =repo["name"]
            if(not fork_status(repo_name)):
                repo_names.append(repo)
    

        print("fetching non fork repo completed")

        forks_list=[]
        resolved_issue=[]
        unresolved_issue=[]
        total_commits_list=[]
        total_contributers =[] 
     
        # Iterate through each repository
        for repo in repo_names:
            print(repo['name'])
            forks_count = fork_count(repo['name'])
            total_commits_count = total_commits(repo['name'])
            resolved_issues_count, unresolved_issues_count = get_repository_issues(username, repo['name'])
            contributors = contributers(repo['name'])
            contributors_count = len(contributors)
         

            forks_list.append(forks_count)
            resolved_issue.append(resolved_issues_count)
            unresolved_issue.append(unresolved_issues_count)
            total_commits_list.append(total_commits_count)
            total_contributers.append(contributors_count)
        
        print("collecting data completed")

       
        Total_Commits_wt =  0.2
        Forks_wt=  0.1
        Resolved_wt= 0.2
        Unresolved_wt=  0.1
        Contributor_wt=  0.1

        prompt = f"""
        **Prompt:**
You are working with a GitHub analyzer tool. The tool requires information about various repositories to determine their complexity. For each repository, you have the following data:
- repo names : {repo_names}
- Total commits: {total_commits_list}
- Forks: {forks_list}
- Resolved issues: {resolved_issue}
- Unresolved issues: {unresolved_issue}
- Contributor count: {total_contributers}

You need to find the name of the most complex repository and its complexity score. The complexity score is calculated based on the following weights:

- Total Commits: {Total_Commits_wt}
- Forks: {Forks_wt}
- Resolved Issues: {Resolved_wt}
- Unresolved Issues: {Unresolved_wt}
- Contributor Count: {Contributor_wt}

Calculate the complexity score for each repository using the provided weights and provide the results in the following format:

"Repository: [repository name], Complexity Score: [complexity score]"

**Example Output:**
Repository: clothing similarity recommendation, Complexity Score: 19481.8
Repository: extra-codes, Complexity Score: 9742.1
Repository: javasorting_algos, Complexity Score: 3871.8



        """
        
        model_resp = analyze_code_complexity(prompt)

        main_resp = {"model_resp": model_resp, "repository_lists": repo_names}
        return main_resp

    except Exception as e:
        
        print(f"An error occurred: {e}")
        return None





analyze_code_complexity
# Streamlit app
def main():
    st.title('GitHub Repository Analyzer')
    user_url = st.text_input("Enter the GitHub user URL")
    username = user_url.split('/')[-1]
    if st.button("Analyze"):
        if user_url:
            main_resp = analyze_github_repository(user_url)
            if main_resp:
                st.write("The most complex repository is", main_resp)
                # st.write("Model output:", main_resp['model_resp'])
                # st.write("Complexity Score:", repository_info['complexity'])
            else:
                st.write("No repositories found or an error occurred.")

if __name__ == '__main__':
    main()

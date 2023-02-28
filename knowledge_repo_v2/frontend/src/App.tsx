import { useState, useEffect } from 'react'
import Header from './components/Header'

const API_URL = process.env.API_URL || 'http://127.0.0.1:5050'

interface Post {
  title: string
  content: string
}

function App() {
  const [posts, setPosts] = useState([{ title: '', content: '' }])

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = () => {
    fetch(`${API_URL}/feed`)
      .then((data) => {
        return data.json()
      })
      .then((postsRes: Post[]) => {
        setPosts(postsRes)
      })
      .catch((err) => {
        console.log(err)
      })
  }

  return (
    <div className="App">
      <>
        <Header title="Knowledge Repo" />
        <h1 className="Info">
          knowledge repo v2
          <br />
          coming soon
        </h1>
        <p>Feel free to reach out to us if you have some ideas about v2?</p>
        {posts.map((post) => {
          return <p>{post.title}</p>
        })}
      </>
    </div>
  )
}

export default App

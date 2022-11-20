import React from 'react'
import { Navbar, Container, Row, Col, Form, Button } from 'react-bootstrap'

const navbarStyle = {
  backgroundColor: '#eeeeee',
}

interface Props {
  title: string
  word?: string
}

const Header = ({ title, word }: Props) => {
  return (
    <>
      <Navbar style={navbarStyle} variant="light">
        <Container className="mt-4">
          <Row className="justify-content-center">
            <Col xs={12} md={8} lg={6}>
              <Form>
                <Row>
                  <Col xs={9}>
                    <Form.Control
                      type="text"
                      value={word}
                      placeholder="Search"
                    />
                    <Button variant="primary" type="submit">
                      Search
                    </Button>
                  </Col>
                </Row>
              </Form>
            </Col>
          </Row>
        </Container>
      </Navbar>
    </>
  )
}

export default Header

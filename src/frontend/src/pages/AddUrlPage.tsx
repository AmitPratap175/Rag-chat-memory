import React, { useState } from 'react';
import { Button, Form, Container, Row, Col } from 'react-bootstrap';

const AddUrlPage: React.FC = () => {
    const [url, setUrl] = useState('');

    const handleAddUrl = () => {
        // Logic to handle the URL addition will be implemented here
        console.log('URL to add:', url);
    };

    return (
        <Container className="mt-4">
            <Row className="justify-content-md-center">
                <Col md={6}>
                    <div className="p-4 rounded bg-dark text-white">
                        <h2 className="text-center mb-4">Add New URL</h2>
                        <Form>
                            <Form.Group className="mb-3" controlId="formBasicEmail">
                                <Form.Label>URL</Form.Label>
                                <Form.Control
                                    type="text"
                                    placeholder="Enter URL"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                />
                            </Form.Group>
                            <div className="d-grid">
                                <Button variant="primary" onClick={handleAddUrl}>
                                    Add URL
                                </Button>
                            </div>
                        </Form>
                    </div>
                </Col>
            </Row>
        </Container>
    );
};

export default AddUrlPage;

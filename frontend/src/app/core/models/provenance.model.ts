export interface ProvenanceRecord {
  entityType: 'location' | 'alert' | 'route' | 'system';
  entityId: number | string;
  entityName: string;
  issuedBy: string;
  issuedAt: string;
  updatedAt: string;
  endpoint: string;
  httpMethod: string;
  dataSource: string;
  status: string;
  provenanceHash: string;
  confidenceScore: number;
}
